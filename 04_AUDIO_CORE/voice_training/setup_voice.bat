@echo off
echo ========================================
echo SISI LOLA VOICE LOCK SETUP
echo Facebook MMS-TTS Yoruba Model
echo ========================================
echo.

echo [1/3] Installing dependencies...
pip install -r requirements.txt

echo.
echo [2/3] Testing voice generation...
python sisi_lola_voice_lock.py

echo.
echo [3/3] Setup complete!
echo.
echo To start the voice API server:
echo   python voice_api.py
echo.
echo Voice samples saved to: generated_samples/
echo ========================================
pause
