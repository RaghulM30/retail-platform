from http.server import HTTPServer, BaseHTTPRequestHandler

VERSION = "4.2.0"
ENVIRONMENT = "DEVELOPMENT"
FEATURE = "Customer Search"

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(f"Retail Platform - Version {VERSION} - {ENVIRONMENT} - {FEATURE}".encode())

server = HTTPServer(("0.0.0.0", 8081), Handler)

print(f"Starting Retail Platform {VERSION} on port 8081")
server.serve_forever()