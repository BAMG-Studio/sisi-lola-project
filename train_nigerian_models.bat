@echo off
REM Sisi Lola Nigerian Training - Windows Quick Start

echo ============================================================
echo SISI LOLA NIGERIAN TRAINING PIPELINE
echo ============================================================

REM Activate virtual environment
if exist .venv_sisi\Scripts\activate.bat (
    call .venv_sisi\Scripts\activate.bat
) else if exist venv_new\Scripts\activate.bat (
    call venv_new\Scripts\activate.bat
) else (
    echo Creating new virtual environment...
    python -m venv .venv_sisi
    call .venv_sisi\Scripts\activate.bat
)

REM Install requirements
echo.
echo Installing dependencies...
pip install -r ml_training\requirements_nigerian.txt

REM Load environment variables
if exist sisi_lola_api\.env (
    echo Loading environment variables...
    for /f "tokens=*" %%a in (sisi_lola_api\.env) do set %%a
)

REM Run setup
echo.
echo Running setup...
python ml_training\scripts\setup_nigerian_models.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Setup failed. Please resolve issues above.
    pause
    exit /b 1
)

REM Run training
echo.
echo Starting training...
python ml_training\scripts\unified_training_orchestrator.py --mode full

echo.
echo ============================================================
echo TRAINING COMPLETE!
echo ============================================================
echo.
echo Check outputs:
echo   - Brain: ml_training\checkpoints\natlas_lora\
echo   - Voice: ml_training\checkpoints\xtts_sisi_lola\
echo   - Config: ml_training\outputs\production_config.json
echo.
pause
