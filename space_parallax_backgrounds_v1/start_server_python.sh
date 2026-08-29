#!/bin/bash
# Simple HTTP server for parallax tester

cd /home/node/.openclaw/workspace-main/tests/parallax_tester

echo "Starting HTTP server on port 8000..."
echo "Open your browser to: http://localhost:8000"
echo "Or use: http://$(hostname -I | awk '{print $1}'):8000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 -m http.server 8000
