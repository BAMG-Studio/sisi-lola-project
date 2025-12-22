from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sisi_lola_api.app.config import SisiLolaDNA
import httpx
import os

router = APIRouter()

class ResearchRequest(BaseModel):
    topic: str

@router.get("/")
async def agent_status():
    return {"status": "Agent Orchestrator Online", "module": "Brain"}

@router.post("/research")
async def research_topic(request: ResearchRequest):
    """
    Uses Perplexity API to fetch real-time information about a topic.
    This gives Sisi Lola 'eyes' on current events.
    """
    perplexity_key = os.getenv("PERPLEXITY_API_KEY")
    
    if not perplexity_key:
        return {
            "status": "simulation",
            "info": f"Simulated research on: {request.topic}. (Add PERPLEXITY_API_KEY to .env for real data)",
            "source": "Internal Knowledge Base"
        }

    # Real implementation for Perplexity API
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": SisiLolaDNA.RESEARCH_MODEL,  # Using best model from config
        "messages": [
            {"role": "system", "content": "You are a research assistant for a virtual host. Find the latest, most relevant details on this topic."},
            {"role": "user", "content": request.topic}
        ]
    }
    headers = {
        "Authorization": f"Bearer {perplexity_key}",
        "Content-Type": "application/json"
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            return {
                "status": "success",
                "info": data['choices'][0]['message']['content'],
                "source": "Perplexity Real-Time Web"
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Research failed: {str(e)}")