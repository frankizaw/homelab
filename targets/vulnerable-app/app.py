#!/usr/bin/env python3
"""
Homelab Vulnerable Web Application (Lab Target)
Pure Python zero-dependency web server for security testing and log analysis.
Outputs standard Nginx/Apache Combined Log Format to disk.
"""

import sys
import os
import time
from datetime import datetime, timezone
import argparse
from urllib.parse import urlparse, parse_qs, unquote
from http.server import HTTPServer, BaseHTTPRequestHandler

# Mock database
USERS = [
    {"id": 1, "username": "admin", "password_hash": "$2b$12$dummyhashforlabtesting001", "role": "administrator"},
    {"id": 2, "username": "operator", "password_hash": "$2b$12$dummyhashforlabtesting002", "role": "security_analyst"},
    {"id": 3, "username": "guest", "password_hash": "$2b$12$dummyhashforlabtesting003", "role": "visitor"}
]

PRODUCTS = {
    "1": {"name": "Sentry Firewall Appliance", "price": "$1299"},
    "2": {"name": "Network Packet Tap", "price": "$450"},
    "3": {"name": "Hardware Security Key", "price": "$65"}
}

FAKE_PASSWD = """root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
webuser:x:1000:1000:Web Application User:/home/webuser:/bin/bash
"""

class TargetHTTPRequestHandler(BaseHTTPRequestHandler):
    log_file_path = None

    def log_message(self, format, *args):
        pass

    def record_access_log(self, status_code, bytes_sent):
        if not self.log_file_path:
            return

        now = datetime.now()
        time_str = now.strftime("%d/%b/%Y:%H:%M:%S +0200")
        client_ip = self.client_address[0]
        method = self.command
        request_uri = self.path
        protocol = self.request_version
        referer = self.headers.get("Referer", "-")
        user_agent = self.headers.get("User-Agent", "-")

        log_line = f'{client_ip} - - [{time_str}] "{method} {request_uri} {protocol}" {status_code} {bytes_sent} "{referer}" "{user_agent}"\n'

        try:
            with open(self.log_file_path, "a", encoding="utf-8") as f:
                f.write(log_line)
                f.flush()
        except Exception as e:
            print(f"[!] Warning: Failed to write access log: {e}", file=sys.stderr)

    def send_html(self, status, content):
        body = content.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        self.record_access_log(status, len(body))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # 1. Reconnaissance / Sensitive file probing
        if path in ["/.env", "/.git/config", "/wp-login.php", "/admin/phpmyadmin/index.php", "/backup.sql"]:
            self.send_html(404, "<h1>404 Not Found</h1><p>The requested URL was not found on this server.</p>")
            return

        # 2. Main home page
        if path == "/" or path == "/index.html":
            html = """
            <!DOCTYPE html>
            <html>
            <head><title>Cyber Homelab - Target App</title></head>
            <body style="font-family: monospace; background: #111; color: #eee; padding: 2rem;">
                <h1>Cyber Homelab Target Application</h1>
                <p>Welcome to the controlled security testing environment.</p>
                <h3>Available Endpoints for Testing:</h3>
                <ul>
                    <li><code>/products?id=1</code> (SQL Injection testbed)</li>
                    <li><code>/search?q=test</code> (Reflected XSS testbed)</li>
                    <li><code>/download?file=readme.txt</code> (Directory Traversal testbed)</li>
                    <li><code>/.env</code>, <code>/.git/config</code>, <code>/wp-login.php</code> (Recon prober endpoints)</li>
                </ul>
            </body>
            </html>
            """
            self.send_html(200, html)
            return

        # 3. SQL Injection endpoint: /products?id=...
        if path == "/products":
            raw_id = query.get("id", [""])[0]
            decoded_id = unquote(raw_id).lower()

            if any(sqli in decoded_id for sqli in ["union", "select", "' or '1'='1", "or 1=1", "/*", "--"]):
                users_dump = "<br>".join([f"ID: {u['id']} | User: {u['username']} | Hash: {u['password_hash']}" for u in USERS])
                html = f"""
                <h2>SQL Database Result (Leaked):</h2>
                <div style="background:#331111; padding:10px; border:1px solid red;">
                    <h3>DUMP: users table</h3>
                    <p>{users_dump}</p>
                </div>
                """
                self.send_html(200, html)
                return

            if raw_id in PRODUCTS:
                p = PRODUCTS[raw_id]
                html = f"<h2>Product: {p['name']}</h2><p>Price: {p['price']}</p>"
                self.send_html(200, html)
                return
            else:
                self.send_html(404, "<h2>Product not found</h2>")
                return

        # 4. Reflected XSS endpoint: /search?q=...
        if path == "/search":
            search_query = query.get("q", [""])[0]
            html = f"""
            <h2>Search Results</h2>
            <p>You searched for: <b>{search_query}</b></p>
            <p>0 results found.</p>
            """
            self.send_html(200, html)
            return

        # 5. Directory Traversal endpoint: /download?file=...
        if path == "/download":
            file_param = query.get("file", [""])[0]
            decoded_file = unquote(file_param)

            if "etc/passwd" in decoded_file or "passwd" in decoded_file:
                self.send_html(200, f"<pre>{FAKE_PASSWD}</pre>")
                return

            if ".." in decoded_file:
                self.send_html(403, "<h2>403 Forbidden: Traversal attempt blocked by OS sandbox.</h2>")
                return

            self.send_html(200, f"<h3>Download: {file_param}</h3><p>File content goes here...</p>")
            return

        # Default 404
        self.send_html(404, "<h1>404 Not Found</h1>")

    def do_POST(self):
        self.send_html(405, "<h1>405 Method Not Allowed</h1>")


def run_server(port=8080, log_file=None):
    if log_file:
        os.makedirs(os.path.dirname(os.path.abspath(log_file)), exist_ok=True)
        TargetHTTPRequestHandler.log_file_path = os.path.abspath(log_file)

    server_address = ("0.0.0.0", port)
    httpd = HTTPServer(server_address, TargetHTTPRequestHandler)
    print(f"[*] Target Application running on http://0.0.0.0:{port}")
    if log_file:
        print(f"[*] Writing Nginx Combined Access Log to: {TargetHTTPRequestHandler.log_file_path}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Server stopped.")
        httpd.server_close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Homelab Vulnerable Web App Server")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on (default: 8080)")
    parser.add_argument("--log-file", type=str, default="logs/access.log", help="Path to access.log")
    parser.add_argument("--daemon", action="store_true", help="Run server as detached background daemon")
    parser.add_argument("--pid-file", type=str, default="", help="Path to write PID file")
    args = parser.parse_args()

    if args.daemon:
        # UNIX double fork daemon pattern
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
        except OSError as e:
            sys.exit(1)

        os.setsid()
        os.umask(0)

        try:
            pid2 = os.fork()
            if pid2 > 0:
                if args.pid_file:
                    with open(args.pid_file, "w") as f:
                        f.write(str(pid2))
                sys.exit(0)
        except OSError as e:
            sys.exit(1)

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, "r")
        so = open(os.devnull, "a+")
        se = open(os.devnull, "a+")
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

    elif args.pid_file:
        with open(args.pid_file, "w") as f:
            f.write(str(os.getpid()))

    run_server(port=args.port, log_file=args.log_file)
