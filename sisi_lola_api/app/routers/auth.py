from __future__ import annotations

import time
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from sisi_lola_api.app.dependencies.auth import require_admin, require_api_key
from sisi_lola_api.app.services import auth_store

router = APIRouter()


class InvitationRequest(BaseModel):
    email: str
    expires_in_days: int = Field(default=14, ge=1, le=90)
    uses: int = Field(default=1, ge=1, le=10)


class RedeemRequest(BaseModel):
    code: str
    email: str
    name: Optional[str] = None


class RotateRequest(BaseModel):
    label: str = "rotated"


@router.post("/auth/invitations")
def create_invitation(body: InvitationRequest, _: bool = Depends(require_admin)):
    auth_store.init_db()
    expires_at = int(time.time()) + body.expires_in_days * 86400
    code = auth_store.create_invite(body.email, expires_at, body.uses)
    return {"code": code, "expires_at": expires_at, "uses": body.uses}


@router.post("/auth/redeem")
def redeem_invitation(body: RedeemRequest):
    auth_store.init_db()
    try:
        api_key, creator_id = auth_store.redeem_invite(body.code, body.email, body.name)
        return {"api_key": api_key, "creator_id": creator_id}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/auth/keys/rotate")
def rotate_api_key(body: RotateRequest, ctx=Depends(require_api_key)):
    auth_store.init_db()
    new_key = auth_store.rotate_key(ctx.creator_id, body.label)
    return {"api_key": new_key}


@router.get("/auth/me")
def get_me(ctx=Depends(require_api_key)):
    return {"creator_id": ctx.creator_id, "api_key_id": ctx.api_key_id, "email": ctx.email}


@router.get("/admin/usage")
def admin_usage(limit: int = 100, creator_id: int | None = None, _: bool = Depends(require_admin)):
    auth_store.init_db()
    return {"usage": auth_store.list_usage(limit=limit, creator_id=creator_id)}


@router.get("/admin/creators")
def admin_creators(_: bool = Depends(require_admin)):
    auth_store.init_db()
    return {"creators": auth_store.list_creators(), "invites": auth_store.list_invites()}
