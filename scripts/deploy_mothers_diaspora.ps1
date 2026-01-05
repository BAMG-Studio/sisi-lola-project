param(
  [switch]$NoSignatureValidation
)

$ErrorActionPreference = 'Stop'

Write-Host "Deploying Mothers in Diaspora WhatsApp (Modal)" -ForegroundColor Cyan

if ($NoSignatureValidation) {
  Write-Host "NOTE: Signature validation should be disabled via Modal env vars/secrets." -ForegroundColor Yellow
}

modal deploy modal_deployments/mothers_diaspora_whatsapp.py

Write-Host "Done. Copy the Modal URL and set Twilio webhook to /twilio/whatsapp" -ForegroundColor Green
