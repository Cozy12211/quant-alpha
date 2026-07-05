#!/usr/bin/env python3
"""Quant Alpha — Agent Hub Local Server (Port 8767)"""
import http.server
import socketserver
import json
import urllib.parse
from pathlib import Path

PORT = 8767
WORKSPACE = Path.home() / "projects" / "quant-alpha"

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/" or path == "/dashboard.html":
            dashboard = WORKSPACE / "dashboard.html"
            if dashboard.exists():
                self.send_file(dashboard, "text/html")
            else:
                self.send_error(404, "dashboard.html not found")
        elif path.startswith("/api/file/"):
            file_path = WORKSPACE / urllib.parse.unquote(path[len("/api/file/"):])
            if file_path.exists() and file_path.is_file():
                self.send_file(file_path, "application/octet-stream")
            else:
                self.send_error(404, "File not found")
        else:
            self.send_error(404)

    def send_file(self, path, content_type):
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        with open(path, 'rb') as f:
            self.wfile.write(f.read())

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"🚀 Quant Alpha Hub running at http://localhost:{PORT}")
        print(f"📁 Project dir: {WORKSPACE}")
        httpd.serve_forever()
