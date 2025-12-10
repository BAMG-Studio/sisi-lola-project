@echo off
REM Run Sisi Lola training on Modal cloud GPU
REM This uses your $30 free Modal credits (~60 training runs)

echo ============================================
echo    SISI LOLA MODAL CLOUD GPU TRAINING
echo ============================================
echo.

REM Check if Modal is authenticated
.venv_training\Scripts\modal.exe token verify
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Modal not authenticated. Run:
    echo   .venv_training\Scripts\modal.exe token new
    exit /b 1
)

echo.
echo Choose training option:
echo   1. Brain training only (faster, ~5 min)
echo   2. Full pipeline - Brain + Voice (~10 min)
echo.
set /p CHOICE="Enter choice (1 or 2): "

echo.
echo Starting Modal cloud training...
echo View progress at: https://modal.com/apps/bamg-studio/main
echo.

if "%CHOICE%"=="2" (
    echo Running full pipeline...
    .venv_training\Scripts\modal.exe run ml_training\modal_train.py --full-pipeline
) else (
    echo Running brain training...
    .venv_training\Scripts\modal.exe run ml_training\modal_train.py
)

echo.
echo ============================================
echo    TRAINING COMPLETE!
echo ============================================
echo.
echo Models pushed to HuggingFace:
echo   - https://huggingface.co/sisilolalive/sisi-lola-brain
echo   - https://huggingface.co/sisilolalive/sisi-lola-voice
echo.
pause
