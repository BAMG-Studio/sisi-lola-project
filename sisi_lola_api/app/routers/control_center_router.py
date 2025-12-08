"""
Control Center routes for Sisi Lola
Asset management, content pipeline, ML operations
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.auth import TokenData, get_current_user, require_permission
from app.database import (
    get_db, Asset, ContentQueue, TrainingJob, 
    PlatformAccount, AuditLog, User
)

router = APIRouter(prefix="/control", tags=["Control Center"])

# Pydantic models for request bodies
class AssetCreate(BaseModel):
    category: str
    subcategory: str
    filename: str
    url: str
    metadata: dict = {}

class ContentCreate(BaseModel):
    title: str
    script: str
    platform: str
    scheduled_at: Optional[datetime] = None
    metadata: dict = {}

class TrainingJobCreate(BaseModel):
    model_type: str
    config: dict = {}

# ============ ASSET MANAGEMENT ============

@router.get("/assets")
async def list_assets(
    category: Optional[str] = None,
    status: Optional[str] = None,
    current_user: TokenData = Depends(require_permission("assets:read")),
    db: Session = Depends(get_db)
):
    """List all assets with optional filters"""
    query = db.query(Asset)
    
    if category:
        query = query.filter(Asset.category == category)
    if status:
        query = query.filter(Asset.status == status)
    
    assets = query.all()
    return {"assets": assets, "count": len(assets)}

@router.post("/assets")
async def create_asset(
    asset_data: AssetCreate,
    current_user: TokenData = Depends(require_permission("assets:write")),
    db: Session = Depends(get_db)
):
    """Create new asset entry"""
    
    # Get user ID
    user = db.query(User).filter(User.email == current_user.email).first()
    
    asset = Asset(
        category=asset_data.category,
        subcategory=asset_data.subcategory,
        filename=asset_data.filename,
        url=asset_data.url,
        metadata_=asset_data.metadata,
        created_by=user.id
    )
    db.add(asset)
    
    # Audit log
    audit = AuditLog(
        user_id=user.id,
        action="create_asset",
        resource=f"asset:{asset.id}",
        details={"category": asset_data.category, "filename": asset_data.filename}
    )
    db.add(audit)
    
    db.commit()
    db.refresh(asset)
    
    return {"message": "Asset created", "asset_id": asset.id}

@router.put("/assets/{asset_id}/status")
async def update_asset_status(
    asset_id: int,
    status: str,
    current_user: TokenData = Depends(require_permission("assets:write")),
    db: Session = Depends(get_db)
):
    """Update asset status (pending, generated, approved, published)"""
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        raise HTTPException(status_code=404, detail="Asset not found")
    
    asset.status = status
    asset.updated_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Status updated", "asset_id": asset_id, "status": status}

# ============ CONTENT PIPELINE ============

@router.get("/content/queue")
async def get_content_queue(
    status: Optional[str] = None,
    platform: Optional[str] = None,
    current_user: TokenData = Depends(require_permission("content:read")),
    db: Session = Depends(get_db)
):
    """Get content queue with filters"""
    query = db.query(ContentQueue)
    
    if status:
        query = query.filter(ContentQueue.status == status)
    if platform:
        query = query.filter(ContentQueue.platform == platform)
    
    content = query.order_by(ContentQueue.scheduled_at).all()
    return {"queue": content, "count": len(content)}

@router.post("/content/queue")
async def add_to_queue(
    content_data: ContentCreate,
    current_user: TokenData = Depends(require_permission("content:write")),
    db: Session = Depends(get_db)
):
    """Add content to queue"""
    user = db.query(User).filter(User.email == current_user.email).first()
    
    content = ContentQueue(
        title=content_data.title,
        script=content_data.script,
        platform=content_data.platform,
        scheduled_at=content_data.scheduled_at,
        metadata_=content_data.metadata,
        created_by=user.id
    )
    db.add(content)
    db.commit()
    db.refresh(content)
    
    return {"message": "Content added to queue", "content_id": content.id}

@router.put("/content/{content_id}/approve")
async def approve_content(
    content_id: int,
    current_user: TokenData = Depends(require_permission("content:approve")),
    db: Session = Depends(get_db)
):
    """Approve content for publishing"""
    user = db.query(User).filter(User.email == current_user.email).first()
    
    content = db.query(ContentQueue).filter(ContentQueue.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    content.status = "approved"
    content.approved_by = user.id
    db.commit()
    
    return {"message": "Content approved", "content_id": content_id}

@router.post("/content/{content_id}/publish")
async def publish_content(
    content_id: int,
    current_user: TokenData = Depends(require_permission("platforms:write")),
    db: Session = Depends(get_db)
):
    """Publish content to platform (triggers actual posting)"""
    content = db.query(ContentQueue).filter(ContentQueue.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    if content.status != "approved":
        raise HTTPException(status_code=400, detail="Content must be approved first")
    
    # TODO: Integrate with actual platform APIs (YouTube, Instagram, TikTok)
    # For now, just update status
    content.status = "published"
    content.published_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Content published", "content_id": content_id}

# ============ ML OPERATIONS ============

@router.get("/ml/jobs")
async def list_training_jobs(
    status: Optional[str] = None,
    current_user: TokenData = Depends(require_permission("ml:read")),
    db: Session = Depends(get_db)
):
    """List ML training jobs"""
    query = db.query(TrainingJob)
    
    if status:
        query = query.filter(TrainingJob.status == status)
    
    jobs = query.order_by(TrainingJob.created_at.desc()).all()
    return {"jobs": jobs, "count": len(jobs)}

@router.post("/ml/train")
async def trigger_training(
    job_data: TrainingJobCreate,
    current_user: TokenData = Depends(require_permission("ml:execute")),
    db: Session = Depends(get_db)
):
    """Trigger ML training job"""
    user = db.query(User).filter(User.email == current_user.email).first()
    
    job = TrainingJob(
        model_type=job_data.model_type,
        status="pending",
        triggered_by=user.id
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    
    # TODO: Integrate with actual training pipeline
    # For now, just create job entry
    
    return {"message": "Training job created", "job_id": job.id}

# ============ PLATFORM MANAGEMENT ============

@router.get("/platforms")
async def list_platforms(
    current_user: TokenData = Depends(require_permission("platforms:read")),
    db: Session = Depends(get_db)
):
    """List connected platform accounts"""
    accounts = db.query(PlatformAccount).all()
    
    # Don't expose credentials
    return {
        "platforms": [
            {
                "id": acc.id,
                "platform": acc.platform,
                "handle": acc.handle,
                "status": acc.status,
                "last_sync": acc.last_sync
            }
            for acc in accounts
        ]
    }

@router.post("/platforms/sync/{platform_id}")
async def sync_platform(
    platform_id: int,
    current_user: TokenData = Depends(require_permission("platforms:write")),
    db: Session = Depends(get_db)
):
    """Sync platform data (followers, posts, analytics)"""
    account = db.query(PlatformAccount).filter(PlatformAccount.id == platform_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Platform not found")
    
    # TODO: Implement actual sync logic
    account.last_sync = datetime.utcnow()
    db.commit()
    
    return {"message": "Platform synced", "platform": account.platform}

# ============ ANALYTICS ============

@router.get("/analytics/dashboard")
async def get_dashboard_metrics(
    current_user: TokenData = Depends(require_permission("analytics:read")),
    db: Session = Depends(get_db)
):
    """Get dashboard metrics"""
    
    # Asset counts
    total_assets = db.query(Asset).count()
    pending_assets = db.query(Asset).filter(Asset.status == "pending").count()
    
    # Content queue
    queue_size = db.query(ContentQueue).filter(ContentQueue.status.in_(["draft", "pending_approval"])).count()
    scheduled_content = db.query(ContentQueue).filter(ContentQueue.status == "scheduled").count()
    
    # ML jobs
    active_jobs = db.query(TrainingJob).filter(TrainingJob.status.in_(["pending", "running"])).count()
    
    return {
        "assets": {
            "total": total_assets,
            "pending": pending_assets
        },
        "content": {
            "queue_size": queue_size,
            "scheduled": scheduled_content
        },
        "ml": {
            "active_jobs": active_jobs
        }
    }
