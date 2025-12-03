"""
Database models and connection for Sisi Lola Control Center
SQLite for development, PostgreSQL for production
"""
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, JSON, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sisi_lola_control.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Association table for many-to-many relationship
user_roles = Table('user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_name', String, ForeignKey('roles.name')),
    Column('assigned_at', DateTime, default=datetime.utcnow),
    Column('assigned_by', Integer, ForeignKey('users.id'), nullable=True)
)

# Models
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    ip_whitelist = Column(JSON, nullable=True)  # Optional IP restrictions
    
    roles = relationship("Role", secondary=user_roles, back_populates="users",
                        foreign_keys=[user_roles.c.user_id, user_roles.c.role_name])
    sessions = relationship("Session", back_populates="user")
    audit_logs = relationship("AuditLog", back_populates="user")

class Role(Base):
    __tablename__ = "roles"
    
    name = Column(String, primary_key=True)
    description = Column(String)
    permissions = Column(JSON)  # List of permissions
    
    users = relationship("User", secondary=user_roles, back_populates="roles",
                        foreign_keys=[user_roles.c.user_id, user_roles.c.role_name])

class Session(Base):
    __tablename__ = "sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    token = Column(String, unique=True, index=True)
    expires_at = Column(DateTime)
    ip_address = Column(String)
    user_agent = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")

class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, index=True)
    subcategory = Column(String, index=True)
    filename = Column(String)
    url = Column(String)
    metadata_ = Column("metadata", JSON)
    status = Column(String, default="pending")  # pending, generated, approved, published
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ContentQueue(Base):
    __tablename__ = "content_queue"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    script = Column(String)
    platform = Column(String)  # youtube, instagram, tiktok
    status = Column(String, default="draft")  # draft, pending_approval, approved, scheduled, published
    scheduled_at = Column(DateTime, nullable=True)
    published_at = Column(DateTime, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    approved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    metadata_ = Column("metadata", JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class PlatformAccount(Base):
    __tablename__ = "platform_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    platform = Column(String)  # youtube, instagram, tiktok
    handle = Column(String)
    credentials_encrypted = Column(String)  # Encrypted JSON
    status = Column(String, default="active")
    last_sync = Column(DateTime, nullable=True)
    metadata_ = Column("metadata", JSON)

class TrainingJob(Base):
    __tablename__ = "training_jobs"
    
    id = Column(Integer, primary_key=True, index=True)
    model_type = Column(String)  # natlas, xtts, whisper
    status = Column(String, default="pending")  # pending, running, completed, failed
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    metrics = Column(JSON)
    triggered_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    action = Column(String)  # login, create_asset, approve_content, etc.
    resource = Column(String)  # Resource affected
    details = Column(JSON)
    ip_address = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="audit_logs")

# Database initialization
def init_db():
    Base.metadata.create_all(bind=engine)
    
    # Create default roles
    db = SessionLocal()
    from app.auth import ROLES
    
    for role_name, role_data in ROLES.items():
        existing = db.query(Role).filter(Role.name == role_name).first()
        if not existing:
            role = Role(
                name=role_name,
                description=role_data["description"],
                permissions=role_data["permissions"]
            )
            db.add(role)
    
    db.commit()
    db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
