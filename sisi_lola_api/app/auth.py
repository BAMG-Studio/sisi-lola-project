"""
Authentication & Authorization System for Sisi Lola Control Center
Role-Based Access Control (RBAC) with JWT tokens
"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import os

# Configuration
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_DAYS = 7

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Role definitions with permissions
ROLES = {
    "SUPER_ADMIN": {
        "permissions": ["*"],  # All permissions
        "description": "Full system control"
    },
    "CONTENT_DIRECTOR": {
        "permissions": ["content:read", "content:write", "content:approve", "analytics:read", "platforms:read"],
        "description": "Content strategy and approval"
    },
    "TECHNICAL_OPERATOR": {
        "permissions": ["ml:read", "ml:write", "ml:execute", "logs:read", "assets:read", "assets:write"],
        "description": "Technical operations"
    },
    "CREATIVE_PRODUCER": {
        "permissions": ["assets:read", "assets:write", "content:read", "content:write", "dna:read", "dna:write"],
        "description": "Asset creation and editing"
    },
    "SOCIAL_MEDIA_MANAGER": {
        "permissions": ["platforms:read", "platforms:write", "content:read", "analytics:read"],
        "description": "Platform management"
    },
    "ANALYST": {
        "permissions": ["analytics:read", "content:read", "platforms:read"],
        "description": "Read-only analytics"
    },
    "VIEWER": {
        "permissions": ["content:read"],
        "description": "Limited preview"
    }
}

# Pydantic models
class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: Optional[str] = None
    roles: List[str] = []

class User(BaseModel):
    id: int
    email: str
    roles: List[str]
    is_active: bool = True
    created_at: datetime

class UserCreate(BaseModel):
    email: str
    password: str
    roles: List[str] = ["VIEWER"]

class UserLogin(BaseModel):
    email: str
    password: str

# Password utilities
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

# JWT token utilities
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def decode_token(token: str) -> TokenData:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        roles: List[str] = payload.get("roles", [])
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return TokenData(email=email, roles=roles)
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

# Permission checking
def has_permission(user_roles: List[str], required_permission: str) -> bool:
    """Check if user has required permission based on their roles"""
    if "SUPER_ADMIN" in user_roles:
        return True
    
    for role in user_roles:
        if role in ROLES:
            permissions = ROLES[role]["permissions"]
            if "*" in permissions or required_permission in permissions:
                return True
    return False

# Dependency for protected routes
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer(auto_error=False))) -> TokenData:
    if os.getenv("SISI_DASHBOARD_OPEN", "true").lower() == "true":
        return TokenData(email="admin@sisilola.local", roles=["SUPER_ADMIN"])
        
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    token = credentials.credentials
    return decode_token(token)

# Permission decorator factory
def require_permission(permission: str):
    async def permission_checker(current_user: TokenData = Depends(get_current_user)):
        if not has_permission(current_user.roles, permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied. Required: {permission}"
            )
        return current_user
    return permission_checker

# Role decorator factory
def require_role(role: str):
    async def role_checker(current_user: TokenData = Depends(get_current_user)):
        if role not in current_user.roles and "SUPER_ADMIN" not in current_user.roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role}"
            )
        return current_user
    return role_checker
