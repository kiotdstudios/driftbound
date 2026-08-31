@echo off
title DRIFTBOUND Server
rem Always run from this script's own folder, wherever it was cloned/downloaded to.
rem (Fixes "The system cannot find the path specified" on any machine that
rem  isn't Diel's own PC -- the old version hardcoded C:\Users\diepowel\...)
cd /d "%~dp0"

echo.
echo  ===================================
echo   DRIFTBOUND - Game Server
echo   http://localhost:8420/driftbound_flight_test.html
echo  ===================================
echo.
echo  Open the link above in your browser.
echo  Keep this window open while playing.
echo.

rem Find a working Python without hardcoding a machine-specific install path.
rem Tries, in order: the official "py" launcher, then "python", then "python3".
rem Skips the Windows-Store "python" stub automatically (it fails --version).
set PYCMD=

py -3 --version >nul 2>nul
if not errorlevel 1 set PYCMD=py -3

if "%PYCMD%"=="" (
  python --version >nul 2>nul
  if not errorlevel 1 set PYCMD=python
)

if "%PYCMD%"=="" (
  python3 --version >nul 2>nul
  if not errorlevel 1 set PYCMD=python3
)

if "%PYCMD%"=="" (
  echo  ERROR: Python was not found on this computer.
  echo.
  echo  Install Python from https://www.python.org/downloads/
  echo  During setup, check the box "Add python.exe to PATH".
  echo  Then close this window and double-click START_GAME.bat again.
  echo.
  pause
  exit /b 1
)

echo  Using Python: %PYCMD%
echo.
%PYCMD% -m http.server 8420 --bind 127.0.0.1
pause
