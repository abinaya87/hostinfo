#!/usr/bin/env python

"""
A simple program that displays the hostname and IP
Great for testing service routing in Kubernetes
"""

from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import argparse
import socket
import signal
import sys

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    """Customize the class to serve the getHostInfo method results"""
    def do_GET(self):
        """Customize the function to serve the getHostInfo method results"""
        self.send_response(200, 'OK')
        self.end_headers()
        self.wfile.write(get_host_info().encode("utf-8"))

def run_web_server(port):
    """Run a webserver the runs forever to respond with the host info"""
    server = "0.0.0.0"
    start_time = datetime.now()
    print(f"Server listening on http://{server}:{port}, started on {start_time}")
    httpd = HTTPServer(('', port), SimpleHTTPRequestHandler)
    httpd.serve_forever()

def terminate(_signal, frame):
    """Ensure server can handle SIGTERM from container runtime"""
    stop_time = datetime.now()
    print(f"Termination requested at {stop_time}, exiting...")
    sys.exit(0)

def get_host_info():
    """Uses socket module to retrieve the hostname & IP"""
    return socket.gethostname() + " " + socket.gethostbyname(socket.gethostname()) + "\n"

def main():
    """Registers signal & args handlers then runs the server"""
    signal.signal(signal.SIGTERM, terminate)
    parser = argparse.ArgumentParser(description='Accept a port number.')
    parser.add_argument('port', default='9898', type=int, nargs='?',
                        help='an integer for the port')
    args = parser.parse_args()
    run_web_server(args.port)

if __name__ == "__main__":
    main()
