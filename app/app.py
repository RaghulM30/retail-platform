from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

VERSION = "4.2.0"
ENVIRONMENT = "DEVELOPMENT"
FEATURE = "Customer Search"

import os

DB_HOST = os.getenv("DB_HOST", "customer-db-uat")
DB_NAME = os.getenv("DB_NAME", "customerdb")
DB_USER = os.getenv("DB_USER", "customeruser")

CUSTOMERS = [
    {"id": 1, "name": "Raghul", "email": "raghul@example.com"},
    {"id": 2, "name": "Arun", "email": "arun@example.com"},
    {"id": 3, "name": "Priya", "email": "priya@example.com"}
]


class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.startswith("/customers"):
    query = parse_qs(urlparse(self.path).query).get("name", [""])[0].lower()

    results = [
        customer["name"]
        for customer in CUSTOMERS
        if query in customer["name"].lower()
    ]

    response = (
    "DB_HOST=" + DB_HOST +
    " | Customers: " + ", ".join(results)
    if results
    else "DB_HOST=" + DB_HOST + " | No customers found"
)
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