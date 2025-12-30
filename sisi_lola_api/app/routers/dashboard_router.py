# =============================================================================
# SISI LOLA UI ROUTER - COMMAND CENTER & DEMO
# =============================================================================
# Handles the delivery of HTML pages for the Sisi Lola ecosystem.
# Routes: /, /dashboard, /demo, /console, /vision
# Last Updated: 2025-12-29
# =============================================================================

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

router = APIRouter(tags=["UI Pages"])

# =============================================================================
# TEMPLATE CONFIGURATION
# =============================================================================
# Setup paths - templates are in sisi_lola_api/app/templates
# Using absolute path resolution for WSL/Windows compatibility
BASE_DIR = Path(__file__).resolve().parent.parent  # sisi_lola_api/app/
TEMPLATE_DIR = BASE_DIR / "templates"

# Debug logging for troubleshooting
logger.info(f"📂 Dashboard Router: BASE_DIR = {BASE_DIR}")
logger.info(f"📂 Dashboard Router: TEMPLATE_DIR = {TEMPLATE_DIR}")
logger.info(f"📂 Dashboard Router: Templates exist = {TEMPLATE_DIR.exists()}")

# Verify templates exist
if TEMPLATE_DIR.exists():
    templates = Jinja2Templates(directory=str(TEMPLATE_DIR))
    logger.info("✅ Jinja2Templates initialized successfully")
else:
    raise RuntimeError(f"Template directory not found: {TEMPLATE_DIR}")

# =============================================================================
# UI ROUTES
# =============================================================================

@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Sisi Lola Home - redirects to dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Sisi Lola Command Center (Admin Dashboard)"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/demo", response_class=HTMLResponse)
async def demo(request: Request):
    """Sisi Lola Public Demo - Chat interface"""
    return templates.TemplateResponse("demo.html", {"request": request})


@router.get("/console", response_class=HTMLResponse)
async def console(request: Request):
    """Developer Console"""
    # Check if console.html exists, fallback to dashboard if not
    if (TEMPLATE_DIR / "console.html").exists():
        return templates.TemplateResponse("console.html", {"request": request})
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/vision", response_class=HTMLResponse)
async def vision_lab(request: Request):
    """Vision Lab - Image Analysis"""
    # Check if vision_lab.html exists, fallback to dashboard if not
    if (TEMPLATE_DIR / "vision_lab.html").exists():
        return templates.TemplateResponse("vision_lab.html", {"request": request})
    return templates.TemplateResponse("dashboard.html", {"request": request})
