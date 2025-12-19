"""
Authentication routes for Sisi Lola Control Center
Login, register, token refresh, user management
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from sisi_lola_api.app.auth import (
    UserCreate, UserLogin, Token, User as UserSchema, TokenData,
    get_password_hash, verify_password, create_access_token, create_refresh_token,
    get_current_user, require_role, require_permission
)
from sisi_lola_api.app.database import get_db, User, Role, Session as DBSession, AuditLog

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register new user (requires SUPER_ADMIN permission in production)"""
    
    # Check if user exists
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Validate roles
    for role in user_data.roles:
        if not db.query(Role).filter(Role.name == role).first():
            raise HTTPException(status_code=400, detail=f"Invalid role: {role}")
    
    # Create user
    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password)
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Assign roles
    for role_name in user_data.roles:
        role = db.query(Role).filter(Role.name == role_name).first()
        user.roles.append(role)
    
    db.commit()
    db.refresh(user)
    
    return UserSchema(
        id=user.id,
        email=user.email,
        roles=[r.name for r in user.roles],
        is_active=user.is_active,
        created_at=user.created_at
    )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, request: Request, db: Session = Depends(get_db)):
    """Login and receive access + refresh tokens"""
    
    # Find user
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account disabled")
    
    # Create tokens
    token_data = {
        "sub": user.email,
        "roles": [r.name for r in user.roles]
    }
    access_token = create_access_token(token_data)
    refresh_token = create_refresh_token(token_data)
    
    # Update last login
    user.last_login = datetime.utcnow()
    
    # Log session
    session = DBSession(
        user_id=user.id,
        token=access_token,
        expires_at=datetime.utcnow(),
        ip_address=request.client.host
    )
    db.add(session)
    
    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="login",
        resource="auth",
        details={"method": "password"},
        ip_address=request.client.host
    )
    db.add(audit)
    
    db.commit()
    
    return Token(access_token=access_token, refresh_token=refresh_token)

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    token_data = decode_token(refresh_token)
    
    user = db.query(User).filter(User.email == token_data.email).first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    new_token_data = {
        "sub": user.email,
        "roles": [r.name for r in user.roles]
    }
    access_token = create_access_token(new_token_data)
    new_refresh_token = create_refresh_token(new_token_data)
    
    return Token(access_token=access_token, refresh_token=new_refresh_token)

@router.get("/me", response_model=UserSchema)
async def get_current_user_info(current_user: TokenData = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get current user information"""
    user = db.query(User).filter(User.email == current_user.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return UserSchema(
        id=user.id,
        email=user.email,
        roles=[r.name for r in user.roles],
        is_active=user.is_active,
        created_at=user.created_at
    )

@router.get("/users", response_model=List[UserSchema])
async def list_users(
    current_user: TokenData = Depends(require_role("SUPER_ADMIN")),
    db: Session = Depends(get_db)
):
    """List all users (SUPER_ADMIN only)"""
    users = db.query(User).all()
    return [
        UserSchema(
            id=u.id,
            email=u.email,
            roles=[r.name for r in u.roles],
            is_active=u.is_active,
            created_at=u.created_at
        )
        for u in users
    ]

@router.put("/users/{user_id}/roles")
async def update_user_roles(
    user_id: int,
    roles: List[str],
    current_user: TokenData = Depends(require_role("SUPER_ADMIN")),
    db: Session = Depends(get_db)
):
    """Update user roles (SUPER_ADMIN only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Clear existing roles
    user.roles = []
    
    # Assign new roles
    for role_name in roles:
        role = db.query(Role).filter(Role.name == role_name).first()
        if not role:
            raise HTTPException(status_code=400, detail=f"Invalid role: {role_name}")
        user.roles.append(role)
    
    db.commit()
    
    return {"message": "Roles updated successfully"}

@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    current_user: TokenData = Depends(require_role("SUPER_ADMIN")),
    db: Session = Depends(get_db)
):
    """Delete user (SUPER_ADMIN only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.delete(user)
    db.commit()
    
    return {"message": "User deleted successfully"}
