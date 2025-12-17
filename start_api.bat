@echo off
REM ============================================================================
REM SISI LOLA API - START SCRIPT (Windows)
REM Launches the unified multimodal API with web demo
REM ============================================================================

echo.
echo ============================================
echo    SISI LOLA - Nigerian AI Virtual Host
echo ============================================
echo.

REM Check if we're in the right directory
if not exist "sisi_lola_api\app\main.py" (
    echo ERROR: Run this from the Sisi_Lola project root
    exit /b 1
)

REM Activate virtual environment
if exist "venv\Scripts\activate.bat" (
    echo Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Set PYTHONPATH
set PYTHONPATH=%PYTHONPATH%;%CD%;%CD%\sisi_lola_api

echo.
echo Starting Sisi Lola API...
echo.
echo Endpoints:
echo   - Web Demo: http://localhost:8000/demo
echo   - API Docs: http://localhost:8000/docs
echo   - Health:   http://localhost:8000/unified/health
echo.
echo Features:
echo   - Brain: Mistral-7B + LoRA (Nigerian languages)
echo   - Personality: Charismatic Nigerian host
echo   - Voice: XTTS-v2 voice synthesis
echo   - Instagram: Webhook integration
echo.
echo ============================================
echo.

cd sisi_lola_api
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
