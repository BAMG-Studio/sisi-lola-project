"""
SISI LOLA UI ROUTER - COMMAND CENTER & DEMO
============================================
Handles the delivery of HTML pages for the Sisi Lola ecosystem.
"""

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(tags=["UI Pages"])

# Setup paths - templates are in sisi_lola_api/app/templates
BASE_DIR = Path(__file__).resolve().parents[1]
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Sisi Lola Command Center (Admin)"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@router.get("/demo", response_class=HTMLResponse)
async def demo(request: Request):
    """Sisi Lola Public Demo"""
    return templates.TemplateResponse("demo.html", {"request": request})

@router.get("/console", response_class=HTMLResponse)
async def console(request: Request):
    return templates.TemplateResponse("console.html", {"request": request})

@router.get("/vision", response_class=HTMLResponse)
async def vision_lab(request: Request):
    return templates.TemplateResponse("vision_lab.html", {"request": request})
