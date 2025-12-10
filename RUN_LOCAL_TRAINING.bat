@echo off
echo ============================================
echo    Sisi Lola Unified Training (Local GPU)
echo ============================================
echo.

cd /d C:\Users\POK28\Dropbox\Sisi_Lola
set PYTHONIOENCODING=utf-8

echo Starting unified training on RTX 3060...
echo This will train both BRAIN and VOICE models.
echo.

.venv_training\Scripts\python.exe ml_training\scripts\train_unified.py --brain-model gpt2

echo.
echo ============================================
echo Training complete!
echo ============================================
pause
