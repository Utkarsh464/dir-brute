#!/usr/bin/env python3
"""Demo server for dir-brute — ~50 paths across every status code + redirects.

Serves a realistic app layout so you can exercise every dir-brute mode on a
single host: plain scan, -f filter, -s save, -R recursion, -t threads,
-v verbose, and --crawl. Includes 200/301/302/307/308/401/403/500 plus 404s.

Run:  python3 demo_server.py [port]   (defaults to 8080)
"""

import random
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# path -> (status, body, location)
# location is only set for 3xx redirects.
ROUTES = {
    # ---- 200: live pages (20) ----
    "/": (
        200,
        "<h1>Home</h1><p>Welcome to the demo app. Use the nav to explore sections.</p>",
    ),
    "/admin": (
        200,
        "<h1>Admin Panel</h1><p>Manage users, roles and system configuration.</p><ul><li>Users</li><li>Settings</li><li>Logs</li></ul>",
    ),
    "/login": (
        200,
        "<h1>Login</h1><p>Sign in with your credentials to continue.</p><form><input placeholder='username'><input placeholder='password' type='password'></form>",
    ),
    "/logout": (
        200,
        "<h1>Logged out</h1><p>You have been signed out successfully.</p>",
    ),
    "/dashboard": (
        200,
        "<h1>Dashboard</h1><p>Overview of recent activity and metrics.</p><ul><li>Active users: 42</li><li>Requests today: 1,204</li></ul>",
    ),
    "/profile": (
        200,
        "<h1>User Profile</h1><p>View and edit your personal information.</p>",
    ),
    "/settings": (
        200,
        "<h1>Settings</h1><p>Configure account and application preferences.</p>",
    ),
    "/users": (200, "<h1>Users</h1><p>All registered accounts in the system.</p>"),
    "/users/list": (
        200,
        "<h1>User List</h1><p>Detailed directory of user accounts.</p><ul><li>alice</li><li>bob</li><li>carol</li></ul>",
    ),
    "/api": (
        200,
        "<h1>API Root</h1><p>Base endpoint for the REST API. See /api/v1 and /api/v2.</p>",
    ),
    "/api/v1": (
        200,
        "<h1>API v1</h1><p>Version 1 of the API. Stable and supported.</p>",
    ),
    "/api/v2": (200, "<h1>API v2</h1><p>Version 2 of the API. New features, beta.</p>"),
    "/api/v1/users": (
        200,
        '<h1>API Users</h1><p>Returns a JSON list of users.</p><pre>[{"id":1,"name":"alice"}]</pre>',
    ),
    "/search": (
        200,
        "<h1>Search</h1><p>Find content across the site.</p><form><input placeholder='query'></form>",
    ),
    "/blog": (200, "<h1>Blog</h1><p>Latest posts and announcements.</p>"),
    "/blog/post": (
        200,
        "<h1>Blog Post</h1><p>Full article content with headings and paragraphs.</p>",
    ),
    "/shop": (200, "<h1>Shop</h1><p>Browse products and add them to your cart.</p>"),
    "/cart": (
        200,
        "<h1>Cart</h1><p>Items you intend to purchase.</p><ul><li>Item A</li><li>Item B</li></ul>",
    ),
    "/checkout": (200, "<h1>Checkout</h1><p>Review your order and pay.</p>"),
    "/products": (
        200,
        "<h1>Products</h1><p>Catalog of available items.</p><ul><li>Widget</li><li>Gadget</li></ul>",
    ),
    # ---- 301: permanent redirects (5) ----
    "/old-admin": (301, "", "/admin"),
    "/old-login": (301, "", "/login"),
    "/home": (301, "", "/"),
    "/www": (301, "", "/"),
    "/secure": (301, "", "/login"),
    # ---- 302: found / temp redirects (5) ----
    "/go": (302, "", "/dashboard"),
    "/redirect": (302, "", "/home"),
    "/auth": (302, "", "/login"),
    "/sso": (302, "", "/login"),
    "/temp": (302, "", "/maintenance"),
    # ---- 307: temporary redirects (3) ----
    "/hold": (307, "", "/login"),
    "/proxy": (307, "", "/api"),
    "/temp-redirect": (307, "", "/dashboard"),
    # ---- 308: permanent redirects (3) ----
    "/legacy": (308, "", "/profile"),
    "/moved": (308, "", "/settings"),
    "/permanent": (308, "", "/admin"),
    # ---- 401: unauthorized (5) ----
    "/secret": (401, "<h1>401 Unauthorized</h1>", None),
    "/admin-panel": (401, "<h1>401 Unauthorized</h1>", None),
    "/internal": (401, "<h1>401 Unauthorized</h1>", None),
    "/private": (401, "<h1>401 Unauthorized</h1>", None),
    "/api/keys": (401, "<h1>401 Unauthorized</h1>", None),
    # ---- 403: forbidden (5) ----
    "/forbidden": (403, "<h1>403 Forbidden</h1>", None),
    "/restricted": (403, "<h1>403 Forbidden</h1>", None),
    "/no-access": (403, "<h1>403 Forbidden</h1>", None),
    "/server-status": (403, "<h1>403 Forbidden</h1>", None),
    "/git": (403, "<h1>403 Forbidden</h1>", None),
    # ---- 500: server error (2) ----
    "/error": (500, "<h1>500 Internal Server Error</h1>", None),
    "/crash": (500, "<h1>500 Internal Server Error</h1>", None),
}

# Unknown paths return a random error/redirect instead of a flat 404,
# so dir-brute output exercises varied status codes (not just 404 strings).
ERROR_POOL = [401, 403, 404, 404, 500, 500, 301, 307]


def wrap_html(title, body):
    """Wrap inner page content in a multi-line HTML document."""
    return (
        "<!DOCTYPE html>\n"
        "<html lang='en'>\n"
        "<head>\n"
        f"  <title>{title}</title>\n"
        "  <meta charset='utf-8'>\n"
        "</head>\n"
        "<body>\n"
        f"  {body}\n"
        "  <footer><p>dir-brute demo server</p></footer>\n"
        "</body>\n"
        "</html>\n"
    )


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if len(path) > 1 and path.endswith("/"):
            path = path[:-1]
        if path in ROUTES:
            entry = ROUTES[path]
            code = entry[0]
            body = entry[1]
            location = entry[2] if len(entry) > 2 else None
            self.send_response(code)
            if location:
                self.send_header("Location", location)
            if body:
                if code == 200:
                    body = wrap_html(path, body)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(body.encode())
            else:
                self.end_headers()
        else:
            code = random.choice(ERROR_POOL)
            self.send_response(code)
            if code in (301, 302, 307, 308):
                self.send_header("Location", "/")
                self.end_headers()
            else:
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"<h1>{code}</h1>".encode())

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    server = ThreadingHTTPServer(("127.0.0.1", port), Handler)
    print(f"dir-brute demo server on http://127.0.0.1:{port}")
    print(f"{len(ROUTES)} routes: 200/301/302/307/308/401/403/500 + 404s")
    print("press Ctrl-C to stop")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped")
