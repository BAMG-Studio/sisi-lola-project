@echo off
cd /d "%~dp0..\.."
.venv\Scripts\python.exe 00_PROJECT_CORE\Scripts\ingest_platform_account.py %*
