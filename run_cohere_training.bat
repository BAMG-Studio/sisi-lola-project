@echo off
REM Cohere Training Automation Script for Windows

echo Starting Cohere Training for Sisi Lola...

cd /d "%~dp0"

REM Check for .env file
if not exist "sisi_lola_api\.env" (
    echo Error: .env file not found
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -q -r ml_training\requirements.txt
pip install -q cohere python-dotenv

REM Run Ansible playbook
echo Running Ansible playbook...
ansible-playbook ansible\playbooks\cohere_training.yml -v

if %ERRORLEVEL% EQU 0 (
    echo Training automation complete!
    echo Check ml_training\logs\ for reports
) else (
    echo Training failed with error code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)
