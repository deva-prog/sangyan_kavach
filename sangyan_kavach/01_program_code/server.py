"""Run:  python server.py   ->  http://localhost:8000   (no dependencies)"""
import json, os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import engine
STATIC = os.path.join(os.path.dirname(os.path.abspath(__file__)), "static")

class H(BaseHTTPRequestHandler):
    def _send(self, code, body, ctype="application/json"):
        b = body if isinstance(body, bytes) else body.encode("utf-8")
        self.send_response(code); self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            return self._send(200, open(os.path.join(STATIC, "index.html"), "rb").read(), "text/html")
        if self.path.startswith("/api/registry"):
            from urllib.parse import urlparse, parse_qs
            q = parse_qs(urlparse(self.path).query).get("q", [""])[0]
            return self._send(200, json.dumps(engine.search_registry(q)))
        if self.path == "/api/drills":
            return self._send(200, json.dumps(engine.DRILLS))
        self._send(404, '{"error":"not found"}')
    def do_POST(self):
        if self.path != "/api/analyse": return self._send(404, '{"error":"not found"}')
        try:
            n = int(self.headers.get("Content-Length", 0))
            d = json.loads(self.rfile.read(n) or b"{}")
            r = engine.analyse(d.get("text", "")[:5000], d.get("name", "")[:100], d.get("lang", "en"))
            self._send(200, json.dumps(r, ensure_ascii=False))
        except Exception as e:
            self._send(400, json.dumps({"error": str(e)}))
    def log_message(self, *a): pass

if __name__ == "__main__":
    import webbrowser
    start = int(os.environ.get("PORT", 8000))
    HOST = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"   # hosting platforms set PORT
    httpd = None
    for port in range(start, start + 20):          # try next port if one is busy
        try:
            httpd = ThreadingHTTPServer((HOST, port), H)
            break
        except OSError:
            print("Port %d is busy, trying the next one..." % port)
    if httpd is None:
        raise SystemExit("Could not find a free port. Close other programs and retry.")
    url = "http://localhost:%d" % port
    print("Sangyan Kavach is running at " + url)
    print("Keep this window open. Press Ctrl+C to stop.")
    try:
        if HOST == "127.0.0.1": webbrowser.open(url)
    except Exception:
        pass
    httpd.serve_forever()
