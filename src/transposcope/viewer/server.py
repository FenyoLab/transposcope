import http.server
import os
import socketserver

web_dir = os.path.join(os.path.dirname(__file__), 'web')

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
