@echo off
echo Installing Python 3.10 for Wav2Lip...
winget install Python.Python.3.10 --silent --accept-package-agreements --accept-source-agreements
echo Python 3.10 installed
echo.
echo Verifying installation...
py -3.10 --version
pause
