import json
from http.server import BaseHTTPRequestHandler, HTTPServer

class Dashboard(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            with open("dashboard/index.html", "rb") as f:
                html = f.read()

            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(html)

        elif self.path == "/alarms":
            with open("alarms.json", "r") as f:
                alarms = f.read()

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(alarms.encode())

server = HTTPServer(("0.0.0.0", 8080), Dashboard)
print("📊 Dashboard çalışıyor: http://127.0.0.1:8080")
server.serve_forever()
