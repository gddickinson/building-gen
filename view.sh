#!/bin/bash
# Launch the interactive 3D building viewer
# Opens a local web server and the viewer in your default browser

cd "$(dirname "$0")"
echo "Starting building viewer at http://localhost:8000/viewer.html"
echo "Press Ctrl+C to stop."
echo ""
python3 -m http.server 8000 &
SERVER_PID=$!
sleep 1
open "http://localhost:8000/viewer.html"
wait $SERVER_PID
