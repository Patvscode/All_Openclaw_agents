#!/usr/bin/env python3
"""Hub server — serves HTTP on 8090 and HTTPS on 8443 for camera/mic access."""
import http.server
import ssl
import os
import sys
import json
import threading
import subprocess
import importlib.util
import time
import base64
import mimetypes
import uuid
import socket
import urllib.error
import urllib.request
from urllib.parse import urlparse
from urllib.parse import parse_qs, unquote, quote

try:
    from PIL import Image
except Exception:
    Image = None

RAWISH_IMAGE_EXTS = {'.dng', '.heic', '.heif', '.tif', '.tiff'}
CHAT_JOB_DIR = os.path.join(os.path.expanduser('~'), '.openclaw', 'hub', 'tmp', 'generative-space-jobs')
IMAGINE_JOB_DIR = os.path.join(os.path.expanduser('~'), '.openclaw', 'hub', 'tmp', 'imagine-studio-jobs')
IMAGINE_API_PORT = int(os.environ.get('IMAGINE_STUDIO_API_PORT', '8112'))
IMAGINE_API_URL = f'http://127.0.0.1:{IMAGINE_API_PORT}'
IMAGINE_API_SCRIPT = os.path.join(os.path.expanduser('~'), '.openclaw', 'hub', 'imagine-studio-api.py')
IMAGINE_API_PYTHON = os.path.join(os.path.expanduser('~'), 'ComfyUI', 'venv', 'bin', 'python')
IMAGINE_API_LOG = os.path.join(os.path.expanduser('~'), '.openclaw', 'hub', 'tmp', 'imagine-studio-api.log')


def read_json_file(path, default=None):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {} if default is None else default


def write_json_file(path, payload):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp_path = f"{path}.tmp"
    with open(tmp_path, 'w', encoding='utf-8') as f:
        json.dump(payload, f)
    os.replace(tmp_path, path)


def chat_job_paths(job_id):
    return {
        'base': os.path.join(CHAT_JOB_DIR, job_id),
        'state': os.path.join(CHAT_JOB_DIR, f'{job_id}.json'),
        'stdout': os.path.join(CHAT_JOB_DIR, f'{job_id}.stdout.log'),
        'stderr': os.path.join(CHAT_JOB_DIR, f'{job_id}.stderr.log'),
    }


def imagine_job_paths(job_id):
    return {
        'base': os.path.join(IMAGINE_JOB_DIR, job_id),
        'state': os.path.join(IMAGINE_JOB_DIR, f'{job_id}.json'),
        'stdout': os.path.join(IMAGINE_JOB_DIR, f'{job_id}.stdout.log'),
        'stderr': os.path.join(IMAGINE_JOB_DIR, f'{job_id}.stderr.log'),
    }


def imagine_api_healthy():
    try:
        req = urllib.request.Request(f'{IMAGINE_API_URL}/health', headers={'User-Agent': 'OpenClaw-Hub/1.0'})
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except Exception:
        return False


def ensure_imagine_api_running(wait_seconds=20):
    if imagine_api_healthy():
        return True
    if not (os.path.isfile(IMAGINE_API_SCRIPT) and os.path.isfile(IMAGINE_API_PYTHON)):
        raise RuntimeError('Imagine Studio API runtime is missing')
    os.makedirs(os.path.dirname(IMAGINE_API_LOG), exist_ok=True)
    with open(IMAGINE_API_LOG, 'ab') as log:
        subprocess.Popen(
            [IMAGINE_API_PYTHON, IMAGINE_API_SCRIPT],
            cwd=os.path.dirname(IMAGINE_API_SCRIPT) or None,
            stdout=log,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    deadline = time.time() + wait_seconds
    while time.time() < deadline:
        if imagine_api_healthy():
            return True
        time.sleep(0.5)
    raise RuntimeError('Imagine Studio API failed to start in time')


def imagine_api_json(method, path, payload=None, timeout=120):
    ensure_imagine_api_running()
    body = None
    headers = {'User-Agent': 'OpenClaw-Hub/1.0'}
    if payload is not None:
        body = json.dumps(payload).encode('utf-8')
        headers['Content-Type'] = 'application/json'
    req = urllib.request.Request(f'{IMAGINE_API_URL}{path}', data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
    return json.loads(raw.decode('utf-8') or '{}')


def is_safe_local_artifact_url(raw_url):
    try:
        parsed = urlparse(str(raw_url or '').strip())
    except Exception:
        return False
    if parsed.scheme != 'http':
        return False
    if parsed.hostname not in {'127.0.0.1', 'localhost'}:
        return False
    return True


def maybe_make_browser_safe_image_variant(path, mime_type):
    ext = os.path.splitext(path)[1].lower()
    if Image is None:
        return None
    if not (str(mime_type).startswith('image/') or ext in RAWISH_IMAGE_EXTS):
        return None
    if ext not in RAWISH_IMAGE_EXTS:
        return None
    try:
        with Image.open(path) as img:
            converted = img.convert('RGB')
            variant = os.path.splitext(path)[0] + '.jpg'
            converted.save(variant, format='JPEG', quality=92)
        return {
            'path': variant,
            'mimeType': 'image/jpeg',
            'name': os.path.basename(variant),
        }
    except Exception:
        return None


class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        super().end_headers()

    def log_message(self, format, *args):
        pass

    def send_json(self, status, data):
        payload = json.dumps(data, default=str).encode()
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', str(len(payload)))
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(payload)

    def send_file(self, path):
        mime_type = mimetypes.guess_type(path)[0] or 'application/octet-stream'
        with open(path, 'rb') as f:
            blob = f.read()
        self.send_response(200)
        self.send_header('Content-Type', mime_type)
        self.send_header('Content-Length', str(len(blob)))
        self.send_header('Cache-Control', 'no-cache')
        self.end_headers()
        self.wfile.write(blob)

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        if path == '/api/ops-discover':
            try:
                spec = importlib.util.spec_from_file_location(
                    "discover",
                    os.path.join(os.path.dirname(__file__) or '.', '35-operations-hub', 'discover.py')
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                data = mod.discover_all()
                self.send_json(200, data)
            except Exception as e:
                self.send_json(500, {"error": str(e)})
            return
        if path == '/api/generative-space/file':
            try:
                query = parse_qs(parsed.query)
                raw_path = unquote((query.get('path') or [''])[0]).strip()
                if not raw_path:
                    raise RuntimeError('Missing path')
                candidate = os.path.realpath(raw_path if os.path.isabs(raw_path) else os.path.join(HUB_DIR, raw_path))
                allowed_roots = [
                    os.path.realpath(HUB_DIR),
                    os.path.realpath(os.path.join(os.path.expanduser('~'), '.openclaw', 'media')),
                ]
                if not any(candidate == root or candidate.startswith(root + os.sep) for root in allowed_roots):
                    raise RuntimeError('Blocked path')
                if not os.path.isfile(candidate):
                    raise RuntimeError('File not found')
                self.send_file(candidate)
            except Exception as e:
                self.send_json(404, {"ok": False, "error": str(e)})
            return
        if path == '/api/generative-space/chat/status':
            try:
                query = parse_qs(parsed.query)
                job_id = ((query.get('id') or [''])[0]).strip()
                if not job_id:
                    raise RuntimeError('Missing id')
                job_paths = chat_job_paths(job_id)
                state = read_json_file(job_paths['state'], default=None)
                if state is None:
                    raise RuntimeError('Job not found')
                self.send_json(200, state)
            except Exception as e:
                self.send_json(404, {"ok": False, "error": str(e)})
            return
        if path == '/api/imagine-studio/file':
            try:
                query = parse_qs(parsed.query)
                raw_path = unquote((query.get('path') or [''])[0]).strip()
                if not raw_path:
                    raise RuntimeError('Missing path')
                candidate = os.path.realpath(raw_path if os.path.isabs(raw_path) else os.path.join(HUB_DIR, raw_path))
                allowed_roots = [
                    os.path.realpath(HUB_DIR),
                    os.path.realpath(os.path.join(os.path.expanduser('~'), 'ComfyUI', 'output')),
                    os.path.realpath(os.path.join(os.path.expanduser('~'), 'ComfyUI', 'input')),
                    os.path.realpath(os.path.join(os.path.expanduser('~'), 'ComfyUI', 'temp')),
                    os.path.realpath(os.path.join(os.path.expanduser('~'), '.openclaw', 'media')),
                ]
                if not any(candidate == root or candidate.startswith(root + os.sep) for root in allowed_roots):
                    raise RuntimeError('Blocked path')
                if not os.path.isfile(candidate):
                    raise RuntimeError('File not found')
                self.send_file(candidate)
            except Exception as e:
                self.send_json(404, {"ok": False, "error": str(e)})
            return
        if path == '/api/imagine-studio/bootstrap':
            try:
                data = imagine_api_json('GET', '/bootstrap', timeout=120)
                self.send_json(200, data)
            except Exception as e:
                self.send_json(500, {"ok": False, "error": str(e)})
            return
        if path == '/api/imagine-studio/models':
            try:
                data = imagine_api_json('GET', '/models', timeout=120)
                self.send_json(200, data)
            except Exception as e:
                self.send_json(500, {"ok": False, "error": str(e)})
            return
        if path == '/api/imagine-studio/jobs':
            try:
                query = parse_qs(parsed.query)
                limit = ((query.get('limit') or ['50'])[0]).strip() or '50'
                data = imagine_api_json('GET', f'/jobs?limit={quote(limit)}', timeout=120)
                self.send_json(200, data)
            except Exception as e:
                self.send_json(500, {"ok": False, "error": str(e)})
            return
        if path.startswith('/api/imagine-studio/jobs/'):
            try:
                backend_path = path.replace('/api/imagine-studio', '', 1)
                data = imagine_api_json('GET', backend_path, timeout=120)
                self.send_json(200, data)
            except Exception as e:
                self.send_json(404, {"ok": False, "error": str(e)})
            return
        if path == '/api/imagine-studio/library':
            try:
                query = parse_qs(parsed.query)
                limit = ((query.get('limit') or ['120'])[0]).strip() or '120'
                data = imagine_api_json('GET', f'/library?limit={quote(limit)}', timeout=120)
                self.send_json(200, data)
            except Exception as e:
                self.send_json(500, {"ok": False, "error": str(e)})
            return
        if path == '/api/imagine-studio/generate/status':
            try:
                query = parse_qs(parsed.query)
                job_id = ((query.get('id') or [''])[0]).strip()
                if not job_id:
                    raise RuntimeError('Missing id')
                data = imagine_api_json('GET', f'/generate/status?id={quote(job_id)}', timeout=120)
                self.send_json(200, data)
            except Exception as e:
                self.send_json(404, {"ok": False, "error": str(e)})
            return
        if path == '/api/generative-space/proxy':
            try:
                query = parse_qs(parsed.query)
                raw_url = unquote((query.get('url') or [''])[0]).strip()
                if not raw_url:
                    raise RuntimeError('Missing url')
                if not is_safe_local_artifact_url(raw_url):
                    raise RuntimeError('Blocked url')
                req = urllib.request.Request(raw_url, headers={'User-Agent': 'OpenClaw-Generative-Space-Proxy/1.0'})
                with urllib.request.urlopen(req, timeout=20) as resp:
                    blob = resp.read()
                    content_type = resp.headers.get('Content-Type', 'application/octet-stream')
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(blob)))
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(blob)
            except Exception as e:
                self.send_json(404, {"ok": False, "error": str(e)})
            return
        return super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path == '/api/generative-space/upload':
            try:
                length = int(self.headers.get('Content-Length', '0') or '0')
                raw = self.rfile.read(length) if length > 0 else b'{}'
                payload = json.loads(raw.decode('utf-8') or '{}')
                name = os.path.basename(str(payload.get('name') or 'upload.bin')).strip() or 'upload.bin'
                mime_type = str(payload.get('type') or 'application/octet-stream')
                data_url = str(payload.get('dataUrl') or '')
                if not data_url.startswith('data:') or ',' not in data_url:
                    raise RuntimeError('Invalid upload payload')
                _, encoded = data_url.split(',', 1)
                blob = base64.b64decode(encoded)
                max_bytes = 20 * 1024 * 1024
                if len(blob) > max_bytes:
                    raise RuntimeError('File too large, max 20 MB')
                upload_dir = os.path.join(HUB_DIR, 'uploads', 'generative-space')
                os.makedirs(upload_dir, exist_ok=True)
                safe_name = ''.join(ch if ch.isalnum() or ch in '._-' else '-' for ch in name).strip('.-') or 'upload.bin'
                target = os.path.join(upload_dir, safe_name)
                stem, ext = os.path.splitext(safe_name)
                counter = 1
                while os.path.exists(target):
                    target = os.path.join(upload_dir, f"{stem}-{counter}{ext}")
                    counter += 1
                with open(target, 'wb') as f:
                    f.write(blob)
                browser_variant = maybe_make_browser_safe_image_variant(target, mime_type)
                browser_path = browser_variant['path'] if browser_variant else target
                browser_type = browser_variant['mimeType'] if browser_variant else mime_type
                browser_name = browser_variant['name'] if browser_variant else os.path.basename(target)
                self.send_json(200, {
                    'ok': True,
                    'attachment': {
                        'name': os.path.basename(target),
                        'originalName': name,
                        'type': mime_type,
                        'originalType': mime_type,
                        'size': len(blob),
                        'path': target,
                        'url': f"/api/generative-space/file?path={browser_path}",
                        'previewPath': browser_path,
                        'previewUrl': f"/api/generative-space/file?path={browser_path}",
                        'previewType': browser_type,
                        'previewName': browser_name,
                        'agentPath': browser_path,
                        'agentType': browser_type,
                        'agentName': browser_name,
                    }
                })
            except Exception as e:
                self.send_json(500, {"ok": False, "error": str(e)})
            return
        if path == '/api/imagine-studio/upload':
            try:
                length = int(self.headers.get('Content-Length', '0') or '0')
                raw = self.rfile.read(length) if length > 0 else b'{}'
                payload = json.loads(raw.decode('utf-8') or '{}')
                name = os.path.basename(str(payload.get('name') or 'upload.bin')).strip() or 'upload.bin'
                mime_type = str(payload.get('type') or 'application/octet-stream')
                data_url = str(payload.get('dataUrl') or '')
                if not data_url.startswith('data:') or ',' not in data_url:
                    raise RuntimeError('Invalid upload payload')
                _, encoded = data_url.split(',', 1)
                blob = base64.b64decode(encoded)
                max_bytes = 24 * 1024 * 1024
                if len(blob) > max_bytes:
                    raise RuntimeError('File too large, max 24 MB')
                upload_dir = os.path.join(HUB_DIR, '45-imagine-studio', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                safe_name = ''.join(ch if ch.isalnum() or ch in '._-' else '-' for ch in name).strip('.-') or 'upload.bin'
                target = os.path.join(upload_dir, safe_name)
                stem, ext = os.path.splitext(safe_name)
                counter = 1
                while os.path.exists(target):
                    target = os.path.join(upload_dir, f"{stem}-{counter}{ext}")
                    counter += 1
                with open(target, 'wb') as f:
                    f.write(blob)
                browser_variant = maybe_make_browser_safe_image_variant(target, mime_type)
                browser_path = browser_variant['path'] if browser_variant else target
                browser_type = browser_variant['mimeType'] if browser_variant else mime_type
                browser_name = browser_variant['name'] if browser_variant else os.path.basename(target)
                self.send_json(200, {
                    'ok': True,
                    'asset': {
                        'name': os.path.basename(target),
                        'originalName': name,
                        'type': mime_type,
                        'size': len(blob),
                        'path': target,
                        'url': f"/api/imagine-studio/file?path={browser_path}",
                        'previewUrl': f"/api/imagine-studio/file?path={browser_path}",
                        'previewType': browser_type,
                        'previewName': browser_name,
                    }
                })
            except Exception as e:
                self.send_json(500, {"ok": False, "error": str(e)})
            return
        if path == '/api/generative-space/chat':
            try:
                length = int(self.headers.get('Content-Length', '0') or '0')
                raw = self.rfile.read(length) if length > 0 else b'{}'
                payload = json.loads(raw.decode('utf-8') or '{}')
                bridge = os.path.join(os.path.dirname(__file__) or '.', 'generative-space-bridge.mjs')
                proc = subprocess.run(
                    ['node', bridge],
                    input=json.dumps(payload),
                    text=True,
                    capture_output=True,
                    timeout=240,
                    cwd=os.path.dirname(bridge) or None,
                )
                stdout = (proc.stdout or '').strip()
                if not stdout:
                    raise RuntimeError((proc.stderr or 'Bridge returned no output').strip())
                data = json.loads(stdout.splitlines()[-1])
                if proc.returncode != 0 or not data.get('ok'):
                    raise RuntimeError(data.get('error') or (proc.stderr or 'Bridge failed').strip())
                self.send_json(200, data)
            except Exception as e:
                self.send_json(500, {"ok": False, "error": str(e)})
            return
        if path == '/api/generative-space/chat/start':
            try:
                length = int(self.headers.get('Content-Length', '0') or '0')
                raw = self.rfile.read(length) if length > 0 else b'{}'
                payload = json.loads(raw.decode('utf-8') or '{}')
                bridge = os.path.join(os.path.dirname(__file__) or '.', 'generative-space-bridge.mjs')
                job_id = str(uuid.uuid4())
                job_paths = chat_job_paths(job_id)
                initial_state = {
                    'ok': True,
                    'jobId': job_id,
                    'status': 'running',
                    'result': None,
                    'error': None,
                }
                write_json_file(job_paths['state'], initial_state)
                launcher = f'''import json, subprocess\nstate_path={job_paths['state']!r}\nstdout_path={job_paths['stdout']!r}\nstderr_path={job_paths['stderr']!r}\nbridge={bridge!r}\npayload={json.dumps(payload)!r}\nstate={{"ok": True, "jobId": {job_id!r}, "status": "running", "result": None, "error": None}}\nwith open(stdout_path, "w", encoding="utf-8") as out, open(stderr_path, "w", encoding="utf-8") as err:\n    proc = subprocess.run(["node", bridge], input=payload, text=True, capture_output=True, timeout=240, cwd={os.path.dirname(bridge) or None!r})\n    out.write(proc.stdout or "")\n    err.write(proc.stderr or "")\n    stdout=(proc.stdout or "").strip()\n    try:\n        data=json.loads(stdout.splitlines()[-1]) if stdout else None\n    except Exception as parse_err:\n        data=None\n        state={{"ok": False, "jobId": {job_id!r}, "status": "error", "result": None, "error": f"Invalid bridge output: {{parse_err}}"}}\n    else:\n        if proc.returncode == 0 and data and data.get("ok"):\n            state={{"ok": True, "jobId": {job_id!r}, "status": "completed", "result": data, "error": None}}\n        else:\n            state={{"ok": False, "jobId": {job_id!r}, "status": "error", "result": data, "error": (data or {{}}).get("error") or (proc.stderr or "Bridge failed").strip()}}\nwith open(state_path + ".tmp", "w", encoding="utf-8") as f:\n    json.dump(state, f)\nimport os\nos.replace(state_path + ".tmp", state_path)\n'''
                subprocess.Popen(['python3', '-c', launcher], cwd=os.path.dirname(bridge) or None, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
                self.send_json(202, initial_state)
            except Exception as e:
                self.send_json(500, {"ok": False, "error": str(e)})
            return
        if path == '/api/imagine-studio/generate/start':
            try:
                length = int(self.headers.get('Content-Length', '0') or '0')
                raw = self.rfile.read(length) if length > 0 else b'{}'
                payload = json.loads(raw.decode('utf-8') or '{}')
                data = imagine_api_json('POST', '/generate/start', payload=payload, timeout=120)
                self.send_json(202, data)
            except urllib.error.HTTPError as e:
                try:
                    body = e.read().decode('utf-8')
                    data = json.loads(body or '{}')
                    message = data.get('detail') or data.get('error') or str(e)
                except Exception:
                    message = str(e)
                self.send_json(500, {"ok": False, "error": message})
            except Exception as e:
                self.send_json(500, {"ok": False, "error": str(e)})
            return
        if path == '/api/imagine-studio/jobs':
            try:
                length = int(self.headers.get('Content-Length', '0') or '0')
                raw = self.rfile.read(length) if length > 0 else b'{}'
                payload = json.loads(raw.decode('utf-8') or '{}')
                data = imagine_api_json('POST', '/jobs', payload=payload, timeout=120)
                self.send_json(202, data)
            except Exception as e:
                self.send_json(500, {"ok": False, "error": str(e)})
            return
        if path.startswith('/api/imagine-studio/jobs/') or path.startswith('/api/imagine-studio/library/'):
            try:
                length = int(self.headers.get('Content-Length', '0') or '0')
                raw = self.rfile.read(length) if length > 0 else b'{}'
                payload = json.loads(raw.decode('utf-8') or '{}')
                backend_path = path.replace('/api/imagine-studio', '', 1)
                data = imagine_api_json('POST', backend_path, payload=payload, timeout=120)
                self.send_json(200, data)
            except Exception as e:
                self.send_json(500, {"ok": False, "error": str(e)})
            return
        self.send_error(404)

HUB_DIR = os.environ.get("CLAWBOARD_HUB_DIR", os.path.join(os.path.expanduser("~"), ".openclaw", "hub"))
os.chdir(HUB_DIR)

# HTTP on 8090 (main, always works)
http_server = http.server.HTTPServer(('0.0.0.0', 8090), NoCacheHandler)

# HTTPS on 8443 (for camera/mic on mobile)
cert_file = os.path.join(HUB_DIR, 'cert.pem')
key_file = os.path.join(HUB_DIR, 'key.pem')

def run_https():
    try:
        https_server = http.server.HTTPServer(('0.0.0.0', 8444), NoCacheHandler)
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        https_server.socket = context.wrap_socket(https_server.socket, server_side=True)
        print("HTTPS serving on :8444 (camera/mic)")
        https_server.serve_forever()
    except Exception as e:
        print(f"HTTPS failed: {e}")

if os.path.exists(cert_file) and os.path.exists(key_file):
    t = threading.Thread(target=run_https, daemon=True)
    t.start()

print("HTTP serving on :8090 (no-cache)")
http_server.serve_forever()
