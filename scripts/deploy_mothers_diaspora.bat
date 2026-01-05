@echo off
setlocal

echo Deploying Mothers in Diaspora WhatsApp (Modal)
echo.

REM Deploy the Modal ASGI app
modal deploy modal_deployments\mothers_diaspora_whatsapp.py

IF %ERRORLEVEL% NEQ 0 (
  echo.
  echo Deployment failed. Check that:
  echo - modal is installed and you are logged in (modal token set / modal setup)
  echo - the secret "twilio-credentials" exists in your Modal account
  exit /b %ERRORLEVEL%
)

echo.
echo Done. In Twilio Sandbox settings, set the webhook to:
echo   https://YOUR-MODAL-URL.modal.run/twilio/whatsapp

echo.
endlocal
