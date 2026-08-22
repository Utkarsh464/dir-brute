#!/usr/bin/env python3
"""Local test server for dir-brute.

Serves a small tree of paths with mixed status codes so you can exercise
every dir-brute mode: plain scan, -f filter, -s save, -R recursion,
-t threads, and --crawl.

Run:  python3 test_server.py [port]   (defaults to 8000)
"""

import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# path -> (status, body). 200/401/403 are seen directly by dir-brute.
# 301/302/307/308 are followed by requests, so dir-brute sees the final
# 200 unless you set allow_redirects=False in brutescrape.py.
PAGES = {
    "/": (200, "<h1>home</h1>"),
    "/admin": (200, "<h1>admin panel</h1>"),
    "/admin/users": (200, "<h1>admin users</h1>"),
    "/admin/users/profile": (200, "<h1>user profile</h1>"),
    "/api": (200, "<h1>api root</h1>"),
    "/api/v1": (200, "<h1>api v1</h1>"),
    "/api/v1/users": (200, "<h1>api users</h1>"),
    "/login": (200, "<h1>login</h1>"),
    "/secret": (401, "<h1>unauthorized</h1>"),
    "/forbidden": (403, "<h1>forbidden</h1>"),
    "/dashboard": (301, ""),
    "/old": (302, ""),
    "/temp": (307, ""),
    "/perm": (308, ""),
}

REDIRECTS = {
    "/dashboard": "/login",
    "/old": "/login",
    "/temp": "/login",
    "/perm": "/login",
}


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if len(path) > 1 and path.endswith("/"):
            path = path[:-1]
        if path in PAGES:
            code, body = PAGES[path]
            if code in (301, 302, 307, 308):
                self.send_response(code)
                self.send_header("Location", REDIRECTS.get(path, "/"))
                self.end_headers()
            else:
                self.send_response(code)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(body.encode())
        else:
            self.send_response(404)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(b"<h1>404 not found</h1>")

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"dir-brute test server on http://127.0.0.1:{port}")
    print("known paths:", ", ".join(sorted(PAGES)))
    print("press Ctrl-C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
