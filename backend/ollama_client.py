"""
Ollama client for SDDS.
Handles LLM communication, system prompt construction, and JSON response parsing.
"""

import json
import os
import re

import httpx

from map_data import get_system_context

OLLAMA_BASE_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────────────────────

_SYSTEM_PROMPT = f"""You are ATLAS (Advanced Tactical Logistics and Analysis System), an AI command assistant integrated into a military C2 (Command and Control) interface with a live operational map.

CRITICAL — RESPONSE FORMAT:
You MUST respond with ONLY valid JSON. No markdown. No code fences. No explanation outside the JSON. Just raw JSON:

{{
  "message": "Your tactical assessment — concise, professional, 1-3 sentences.",
  "map_commands": []
}}

{get_system_context()}

═══ AVAILABLE MAP COMMANDS ═══
Include these objects in the "map_commands" array to update the live map.

1. Drop a pin marker:
{{"type":"drop_pin","id":"<unique_id>","coords":[lon,lat],"label":"Label","color":"amber|green|red|cyan|white"}}

2. Highlight a zone (filled polygon):
{{"type":"highlight_zone","id":"<unique_id>","coords":[[lon,lat],...],"color":"amber|green|red|cyan","label":"Zone Name","opacity":0.35}}

3. Highlight a named road by route ID (looks up coords automatically):
{{"type":"highlight_road","id":"<unique_id>","route_id":"MSR_TIGER|ROUTE_COBRA|ROUTE_FALCON|SUPPLY_DELTA","color":"amber|green|red|cyan|white","width":3}}

4. Draw a custom path/route line:
{{"type":"trace_path","id":"<unique_id>","coords":[[lon,lat],...],"color":"amber|green|red|cyan|white","label":"Path Name","width":3}}

5. Clear overlay layers:
{{"type":"clear_layer","layer":"pins|zones|paths|all"}}

6. Pan and zoom the map to fit a set of coordinates:
{{"type":"fit_to_zone","coords":[[lon,lat],...] }}

7. Add a floating text label on the map:
{{"type":"add_label","id":"<unique_id>","coords":[lon,lat],"text":"Label text","color":"amber|green|cyan|red|white"}}

═══ COLOR CONVENTIONS ═══
green  → friendly forces, safe zones
red    → hostile / enemy / danger
amber  → neutral, supply, points of interest
cyan   → routes, paths, observation posts, camping zones
white  → general labels

═══ RULES ═══
- Always use unique IDs per command (e.g. "pin_alpha_1", "zone_bravo", "path_msr")
- Clear relevant layers before adding new overlays when a fresh view is appropriate
- When asked about paths, trace the recommended route AND explain the trade-offs briefly
- When asked about zones, highlight the relevant polygons and zoom to them
- Keep the "message" field brief — the map does the visual work
- Respond as ATLAS: tactical, precise, no filler words
- ALWAYS return valid JSON — if unsure, return empty map_commands array
"""


# ─────────────────────────────────────────────────────────────────────────────
# MODEL DETECTION
# ─────────────────────────────────────────────────────────────────────────────

_PREFERRED = [
    "llama3", "llama3.2", "llama3.1",
    "mistral", "gemma3", "gemma2", "gemma",
    "phi4", "phi3", "phi", "qwen", "deepseek",
]


async def get_available_model() -> str:
    """Auto-detect the best available Ollama model."""
    env_model = os.getenv("OLLAMA_MODEL")
    if env_model:
        return env_model

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            resp.raise_for_status()
            models: list[dict] = resp.json().get("models", [])
            if not models:
                return "llama3.2"

            for prefix in _PREFERRED:
                for m in models:
                    if m["name"].lower().startswith(prefix):
                        return m["name"]

            return models[0]["name"]
    except Exception:
        return "llama3.2"


# ─────────────────────────────────────────────────────────────────────────────
# RESPONSE PARSING
# ─────────────────────────────────────────────────────────────────────────────

def parse_llm_response(text: str) -> dict:
    """
    Robustly extract JSON from LLM output.
    Handles raw JSON, markdown code fences, and partial wrapping.
    """
    text = text.strip()

    # 1. Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Strip markdown code fences: ```json ... ``` or ``` ... ```
    match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if match:
        try:
            return json.loads(match.group(1).strip())
        except json.JSONDecodeError:
            pass

    # 3. Find first { ... } block
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass

    # 4. Fallback — return the raw text as a plain message
    return {"message": text, "map_commands": []}


# ─────────────────────────────────────────────────────────────────────────────
# CHAT
# ─────────────────────────────────────────────────────────────────────────────

async def chat(message: str, map_context: dict, model: str | None = None) -> dict:
    """Send a user message to Ollama and return a structured response dict."""
    if model is None:
        model = await get_available_model()

    # Append current map state so the LLM knows what's visible
    context_suffix = ""
    if map_context:
        context_suffix = f"\n\nCURRENT MAP STATE: {json.dumps(map_context)}"

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": message + context_suffix},
        ],
        "stream": False,
        "options": {
            "temperature": 0.2,   # Low for reliable JSON
            "num_predict": 1024,
        },
    }

    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(f"{OLLAMA_BASE_URL}/api/chat", json=payload)
        resp.raise_for_status()

    content: str = resp.json().get("message", {}).get("content", "")
    return parse_llm_response(content)


# ─────────────────────────────────────────────────────────────────────────────
# STATUS
# ─────────────────────────────────────────────────────────────────────────────

async def check_ollama_status() -> dict:
    """Return Ollama connectivity status and available models."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            resp = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            resp.raise_for_status()
            models = [m["name"] for m in resp.json().get("models", [])]
            return {"online": True, "models": models}
    except Exception as exc:
        return {"online": False, "error": str(exc), "models": []}
