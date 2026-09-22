from http.server import HTTPServer, BaseHTTPRequestHandler

VERSION = "4.2.0"
ENVIRONMENT = "DEVELOPMENT"
FEATURE = "Customer Search"

CUSTOMERS = [
    {"id": 1, "name": "Raghul", "email": "raghul@example.com"},
    {"id": 2, "name": "Arun", "email": "arun@example.com"},
    {"id": 3, "name": "Priya", "email": "priya@example.com"}
]


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == "/customers":
    		response = "Customer Search Service - Ready"
	elif self.path == "/payment":
    		response = "Payment Service: FIXED - Payment processing is working"
	else:
    		response = f"Retail Platform - Version {VERSION} - {ENVIRONMENT} - {FEATURE}"

        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(response.encode())


server = HTTPServer(("0.0.0.0", 8081), Handler)

print(f"Starting Retail Platform {VERSION} on port 8081")
server.serve_forever()