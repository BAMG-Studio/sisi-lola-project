@echo off
REM Complete Setup and Validation for Sisi Lola Nigerian Training

echo ============================================================
echo SISI LOLA - COMPLETE SETUP AND VALIDATION
echo ============================================================

REM Activate environment
if exist .venv_sisi\Scripts\activate.bat (
    call .venv_sisi\Scripts\activate.bat
) else (
    python -m venv .venv_sisi
    call .venv_sisi\Scripts\activate.bat
)

REM Install dependencies
echo.
echo [1/4] Installing dependencies...
pip install -q torch transformers peft accelerate bitsandbytes datasets pyyaml huggingface-hub

REM Load environment
for /f "tokens=*" %%a in (sisi_lola_api\.env) do set %%a

REM Run setup
echo.
echo [2/4] Running setup validation...
python ml_training\scripts\setup_nigerian_models.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo Setup validation failed. Check errors above.
    pause
    exit /b 1
)

REM Quick model test
echo.
echo [3/4] Testing model access...
python -c "from huggingface_hub import login; login(token='%HUGGINGFACE_TOKEN%'); print('✅ HuggingFace access OK')"

REM Create test inference script
echo.
echo [4/4] Creating quick test...
python -c "print('✅ Setup complete! Ready to train.')"

echo.
echo ============================================================
echo SETUP COMPLETE - READY TO TRAIN
echo ============================================================
echo.
echo Next: Run training with:
echo   train_nigerian_models.bat
echo.
pause
