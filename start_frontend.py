#!/usr/bin/env python3
import http.server
import socketserver
import os
import sys

# Change to frontend directory
os.chdir('frontend')

PORT = 5500
Handler = http.server.SimpleHTTPRequestHandler

# Try to reuse the address
class ReuseAddrTCPServer(socketserver.TCPServer):
    allow_reuse_address = True

try:
    with ReuseAddrTCPServer(("localhost", PORT), Handler) as httpd:
        print(f"Frontend server running at http://localhost:{PORT}/")
        print("Press Ctrl+C to stop")
        httpd.serve_forever()
except OSError as e:
    if "Address already in use" in str(e):
        print(f"\nPort {PORT} is already in use!")
        print("This might be VS Code Live Server.")
        print("\nYou can either:")
        print("1. Open http://localhost:5500 in your browser (if VS Code Live Server is running)")
        print("2. Stop VS Code Live Server and run this script again")
        print("3. Or just open the index.html file directly in your browser")
        sys.exit(1)
    else:
        raise