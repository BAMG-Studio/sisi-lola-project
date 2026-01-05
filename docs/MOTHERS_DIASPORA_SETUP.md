# Mothers in Diaspora (WhatsApp) — Modal + Twilio

## What this is
A minimal Phase 1 WhatsApp webhook on Modal that:
- Receives inbound Twilio WhatsApp messages
- Validates Twilio signatures (optional disable for testing)
- Runs a lightweight router (text vs voice/media, intent + language heuristics)
- Replies with TwiML

## Files
- `modal_deployments/mothers_diaspora_whatsapp.py`
- `modal_deployments/mothers_diaspora_router.py`

## Modal secret
Create a Modal secret named `TWILIO_CREDENTIALS` with these env vars:
- `TWILIO_ACCOUNT_SID`
- `TWILIO_AUTH_TOKEN` (or `TWILIO_AUTH_TOKEN_LIVE`)
- `TWILIO_WHATSAPP_FROM` (example: `whatsapp:+14155238886`)

Example:
```bash
modal secret create TWILIO_CREDENTIALS \
  TWILIO_ACCOUNT_SID="..." \
  TWILIO_AUTH_TOKEN="..." \
  TWILIO_WHATSAPP_FROM="whatsapp:+14155238886"
```

## Deploy
```bash
modal deploy modal_deployments/mothers_diaspora_whatsapp.py
```

Modal will output the public URL for the ASGI app.

## Twilio console
In the Twilio WhatsApp Sandbox settings:
- Set **When a message comes in** to:
  - `https://<your-modal-app>.modal.run/twilio/whatsapp`

## Testing
- Join the sandbox from WhatsApp.
- Send a text message and confirm you get a reply.

## Notes
If you are testing behind a proxy/tunnel and signature validation breaks, you can temporarily disable it by setting:
- `DISABLE_TWILIO_SIGNATURE_VALIDATION=true`

(Do not leave this disabled for production.)
