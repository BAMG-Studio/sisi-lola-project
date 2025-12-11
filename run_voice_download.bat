@echo off
echo Starting Voice Dataset Download...
cd /d "%~dp0"
call .venv\Scripts\activate
python download_fleurs.py
echo.
echo Download complete! Press any key to close...
pause > nul
