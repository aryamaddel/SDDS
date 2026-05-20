"""
SDDS FastAPI backend.
Exposes /chat, /health, and /api/map-data endpoints.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

from ollama_client import chat, check_ollama_status, get_available_model
from map_data import get_map_data

app = FastAPI(title="SDDS Backend", version="1.0.0")

# Allow all origins — this is a local dev / LAN app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────────────────────────
# SCHEMAS
# ─────────────────────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    map_context: Optional[dict] = None


class ChatResponse(BaseModel):
    message: str
    map_commands: list
    model_used: Optional[str] = None


# ─────────────────────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    """Check backend and Ollama connectivity."""
    ollama = await check_ollama_status()
    model = None
    if ollama["online"]:
        model = await get_available_model()
    return {
        "status": "ok",
        "ollama": ollama,
        "model": model,
    }


@app.post("/chat", response_model=ChatResponse)
async def handle_chat(req: ChatRequest):
    """
    Send a message to ATLAS (Ollama LLM) with current map context.
    Returns an AI message and a list of map commands to execute on the frontend.
    """
    model = await get_available_model()
    try:
        result = await chat(
            message=req.message,
            map_context=req.map_context or {},
            model=model,
        )
        return ChatResponse(
            message=result.get("message", "No response from ATLAS."),
            map_commands=result.get("map_commands", []),
            model_used=model,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/map-data")
async def get_map():
    """Return pre-loaded tactical data (zones, routes, landmarks)."""
    return get_map_data()
