"""
DRIFTBOUND local dev server — run this instead of opening the HTML directly.
Visit: http://localhost:8080/driftbound_flight_test.html
Share with LAN friend: http://YOUR_IP:8080/driftbound_flight_test.html
"""
import http.server, socketserver, os, webbrowser, socket

PORT = 8080
os.chdir(os.path.dirname(os.path.abspath(__file__)))

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "unknown"

class Handler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # quiet mode — suppress request spam

print("=" * 52)
print("  DRIFTBOUND LOCAL SERVER")
print("=" * 52)
print(f"  Local:  http://localhost:{PORT}/driftbound_flight_test.html")
print(f"  LAN:    http://{get_local_ip()}:{PORT}/driftbound_flight_test.html")
print("  Press Ctrl+C to stop")
print("=" * 52)

webbrowser.open(f"http://localhost:{PORT}/driftbound_flight_test.html")

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    httpd.serve_forever()
