@echo off
echo ============================================================
echo SISI LOLA CONTROL CENTER - PRODUCTION TEST SUITE
echo ============================================================
echo.

python run_tests.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo SUCCESS! System is production-ready
    echo ============================================================
    echo.
    echo Next steps:
    echo 1. Review coverage report: htmlcov\index.html
    echo 2. Deploy: python deploy_production.py
    echo 3. Start server: cd sisi_lola_api ^&^& uvicorn app.main:app --reload
) else (
    echo.
    echo ============================================================
    echo FAILED! Fix issues before deploying
    echo ============================================================
)

pause
