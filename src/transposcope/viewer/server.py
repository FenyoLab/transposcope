"""
File: server.py
Author: Mark Grivainis
Email: mark.grivainis@fenyolab.org
Github: https://github.com/MarkGrivainis
Description: Local server for files generated by TranspoScope.
             Due to the TranspoScope web page using ajax requests a web server
             is required.
"""

import http.server
import os
import socketserver

WEB_DIR = os.path.join(os.path.dirname(__file__), "web")

PORT = 8000
Handler = http.server.SimpleHTTPRequestHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print("serving at port", PORT)
    httpd.serve_forever()
