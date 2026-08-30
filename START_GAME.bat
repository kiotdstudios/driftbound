@echo off
title DRIFTBOUND Server
cd /d "C:\Users\diepowel\Documents\DRIFTBOUND"
echo.
echo  ===================================
echo   DRIFTBOUND - Game Server
echo   http://localhost:8420/driftbound_flight_test.html
echo  ===================================
echo.
echo  Open the link above in your browser.
echo  Keep this window open while playing.
echo.
"C:\Program Files\Python313\python.exe" -m http.server 8420 --bind 127.0.0.1
pause
