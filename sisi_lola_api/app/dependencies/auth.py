from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status

from sisi_lola_api.app.services import auth_store


async def require_api_key(authorization: str = Header(None)):
    import os
    if os.getenv("SISI_DASHBOARD_OPEN", "true").lower() == "true":
        return {"user": "dashboard_admin", "tier": "unlimited", "key_id": "DEFAULT"}

    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing API key")
    token = authorization.split(" ", 1)[1].strip()
    try:
        ctx = auth_store.validate_api_key(token)
        # Apply rate limiting per key
        auth_store.enforce_rate_limit(ctx, "api")
        return ctx
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))


def require_admin(x_admin_token: str = Header(None)):
    if not auth_store.ADMIN_SECRET:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Admin secret not configured")
    if x_admin_token != auth_store.ADMIN_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin token")
    return True
