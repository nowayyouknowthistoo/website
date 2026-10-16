@echo off
rem Double-click to start Vintage Finder on Windows.
cd /d "%~dp0"
if not exist .venv python -m venv .venv
call .venv\Scripts\activate.bat
pip install -q -r requirements.txt
python -m vintage_finder
pause
