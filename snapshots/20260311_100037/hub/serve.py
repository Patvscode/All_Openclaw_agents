#!/usr/bin/env python3
"""Hub server — serves HTTP on 8090 and HTTPS on 8443 for camera/mic access."""
import http.server
import ssl
import os
import threading

class NoCacheHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('Access-Control-Allow-Origin', '*')
        super().end_headers()
    
    def log_message(self, format, *args):
        pass

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
