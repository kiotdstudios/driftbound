@echo off
title DRIFTBOUND Server (modular build)
REM ── LAUNCHER RECOVERY (Test Harness Migration checkpoint) ──────────────────
REM Previous version pointed at the legacy monolith folder (DRIFTBOUND) and a
REM Python interpreter path that does not exist on this machine. Fixed to:
REM   1) run from the modular repo (this folder — contains index.html)
REM   2) use the real installed Python 3.12 interpreter, with PATH fallback
REM   3) auto-open the browser (after a short delay so the server is up first)
cd /d "%~dp0"

set "PYEXE=C:\Users\diepowel\AppData\Local\Programs\Python\Python312\python.exe"
if not exist "%PYEXE%" set "PYEXE=py"
if not exist "%PYEXE%" set "PYEXE=python"

echo.
echo  ===================================
echo   DRIFTBOUND - Game Server (modular)
echo   http://localhost:8420/index.html
echo  ===================================
echo.
echo  This window IS the game server — keep it open while playing.
echo  Your browser will open automatically in a couple seconds...
echo.

REM Detached helper: wait briefly for the server to bind, then open the browser.
REM Runs independently so the line below (the actual server) can start immediately.
start "" cmd /c "timeout /t 2 >nul & start "" "http://localhost:8420/index.html""

"%PYEXE%" -m http.server 8420 --bind 127.0.0.1
pause
