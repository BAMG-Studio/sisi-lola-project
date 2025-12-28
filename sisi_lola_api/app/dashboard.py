"""
SISI LOLA COMMAND CENTER - UI
==============================
A high-performance, premium dashboard for:
- Content Generation (Radio, Story-world)
- Multimodal Testing (Vision, Voice)
- Gist Hunting & Data Curation
- Social Token Management
"""

import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

app = FastAPI(title="Sisi Lola Command Center")

# Setup paths
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Ensure static directory exists
(BASE_DIR / "static").mkdir(exist_ok=True)

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/console", response_class=HTMLResponse)
async def console(request: Request):
    return templates.TemplateResponse("console.html", {"request": request})

@app.get("/vision", response_class=HTMLResponse)
async def vision_lab(request: Request):
    return templates.TemplateResponse("vision_lab.html", {"request": request})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
