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

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def log_message(self, format, *args):
        pass

    def do_GET(self):
        if self.path == '/api/ops-discover':
            try:
                spec = importlib.util.spec_from_file_location(
                    "discover",
                    os.path.join(os.path.dirname(__file__) or '.', '35-operations-hub', 'discover.py')
                )
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)
                data = mod.discover_all()
                payload = json.dumps(data, default=str).encode()
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Content-Length', str(len(payload)))
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Cache-Control', 'no-cache')
                self.end_headers()
                self.wfile.write(payload)
            except Exception as e:
                err = json.dumps({"error": str(e)}).encode()
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(err)
            return
        return super().do_GET()

os.chdir('/home/pmello/.openclaw/hub')

# HTTP on 8090 (main, always works)
http_server = http.server.HTTPServer(('0.0.0.0', 8090), NoCacheHandler)

# HTTPS on 8443 (for camera/mic on mobile)
cert_file = '/home/pmello/.openclaw/hub/cert.pem'
key_file = '/home/pmello/.openclaw/hub/key.pem'

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
