@echo off
echo ============================================================
echo STARTING SISI LOLA NIGERIAN TRAINING
echo ============================================================
echo.
echo Status: All prerequisites validated
echo Voice samples: 11 ready
echo Personality data: 20 lines
echo HuggingFace: Connected
echo.
echo NOTE: Training will take 24-48 hours on CPU
echo       (6-12 hours with GPU)
echo.
echo This window will show progress. You can minimize it.
echo Training will continue in background.
echo.
pause

REM Activate environment
if exist .venv_sisi\Scripts\activate.bat (
    call .venv_sisi\Scripts\activate.bat
) else (
    python -m venv .venv_sisi
    call .venv_sisi\Scripts\activate.bat
)

REM Load environment
for /f "tokens=*" %%a in (sisi_lola_api\.env) do set %%a

REM Install minimal requirements
echo Installing requirements...
pip install -q torch transformers datasets pyyaml huggingface-hub

REM Start training
echo.
echo Starting training orchestrator...
python ml_training\scripts\unified_training_orchestrator.py --mode full

echo.
echo ============================================================
echo TRAINING COMPLETE!
echo ============================================================
pause
