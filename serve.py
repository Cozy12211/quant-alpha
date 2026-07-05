#!/usr/bin/env python3
"""Quant Alpha — Agent Hub Local Server (Port 8767)"""
import http.server
import socketserver
import json
import urllib.parse
import sys
from pathlib import Path

PORT = 8767
WORKSPACE = Path.home() / "projects" / "quant-alpha"

# 添加项目目录到路径，导入quote模块
sys.path.insert(0, str(WORKSPACE))

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
        elif path == "/trade-log.html":
            log_page = WORKSPACE / "trade-log.html"
            if log_page.exists():
                self.send_file(log_page, "text/html")
            else:
                self.send_error(404, "trade-log.html not found")
        elif path.startswith("/api/quote/"):
            symbol = path[len("/api/quote/"):]
            self.handle_quote(symbol)
        elif path.startswith("/api/file/"):
            file_path = WORKSPACE / urllib.parse.unquote(path[len("/api/file/"):])
            if file_path.exists() and file_path.is_file():
                self.send_file(file_path, "application/octet-stream")
            else:
                self.send_error(404, "File not found")
        else:
            self.send_error(404)

    def handle_quote(self, symbol):
        """获取股票实时行情"""
        try:
            # 动态导入避免启动时依赖问题
            import importlib.util
            quote_path = WORKSPACE / "quote.py"
            if not quote_path.exists():
                self.send_json({"error": "quote.py not found"}, 500)
                return
                
            spec = importlib.util.spec_from_file_location("quote", quote_path)
            quote_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(quote_mod)
            
            result = quote_mod.get_quote(symbol)
            if result:
                self.send_json(result)
            else:
                self.send_json({"error": f"无法获取 {symbol} 的行情"}, 404)
        except Exception as e:
            self.send_json({"error": str(e)}, 500)

    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

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
