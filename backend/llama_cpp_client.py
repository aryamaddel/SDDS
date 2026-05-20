"""
llama_cpp_client.py - SDDS Backend
Offline CPU-optimized LLM client using llama-cpp-python.
Handles lazy loading, prompt construction, and non-blocking inference.
"""

import os
import json
import re
import anyio
from typing import Optional
from map_data import get_system_context

# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM PROMPT ( ATLAS Persona )
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
# MODEL LIFECYCLE MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

_llm = None

def get_model_path() -> str:
    """Retrieve model path from environment variable or standard location."""
    default_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "models",
        "qwen2.5-3b-instruct-q4_k_m.gguf"
    )
    return os.getenv("SDDS_MODEL_PATH", default_path)

def get_model_name() -> str:
    """Get the model file name for UI display."""
    return os.path.basename(get_model_path())

def init_llm():
    """Lazy initializer for Llama model. Loads GGUF into memory."""
    global _llm
    if _llm is not None:
        return _llm

    model_path = get_model_path()
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Local GGUF model not found at: {model_path}\n"
            f"Please run download_model.bat first to download the model."
        )

    print(f"\n[..] Initializing local CPU LLM from: {model_path}")
    from llama_cpp import Llama
    
    # Optimize for pure CPU execution on typical multi-core machines
    _llm = Llama(
        model_path=model_path,
        n_ctx=4096,
        n_threads=max(1, os.cpu_count() or 4),
        n_gpu_layers=0,  # Pure CPU
        verbose=False,
    )
    print(f"[OK] Model successfully loaded into memory.\n")
    return _llm

# ─────────────────────────────────────────────────────────────────────────────
# PARSING UTILITIES
# ─────────────────────────────────────────────────────────────────────────────

def parse_llm_response(text: str) -> dict:
    """Robustly extract JSON from LLM output."""
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
# CHAT INFERENCE
# ─────────────────────────────────────────────────────────────────────────────

def _sync_chat(message: str, map_context: dict) -> dict:
    """Synchronous inference worker function."""
    llm = init_llm()

    context_suffix = ""
    if map_context:
        context_suffix = f"\n\nCURRENT MAP STATE: {json.dumps(map_context)}"

    # Construct the chat message structure
    messages = [
        {"role": "system", "content": _SYSTEM_PROMPT},
        {"role": "user", "content": message + context_suffix}
    ]

    # Run chat completion using llama_cpp API
    # Max tokens is 1024 to fit any detailed command list + tactical assessment
    response = llm.create_chat_completion(
        messages=messages,
        temperature=0.2,       # Low temperature ensures reliable JSON obedience
        max_tokens=1024,
    )

    content = response["choices"][0]["message"]["content"]
    return parse_llm_response(content)

async def chat(message: str, map_context: dict, model: str | None = None) -> dict:
    """
    Asynchronous chat interface.
    Offloads heavy CPU inference to a background thread to prevent blocking FastAPI.
    """
    # anyio.to_thread.run_sync offloads the blocking execution to a worker thread pool.
    return await anyio.to_thread.run_sync(_sync_chat, message, map_context)

# ─────────────────────────────────────────────────────────────────────────────
# STATUS / HEALTH
# ─────────────────────────────────────────────────────────────────────────────

async def check_model_status() -> dict:
    """Return model status and path details for health endpoint."""
    path = get_model_path()
    exists = os.path.exists(path)
    return {
        "online": exists,
        "models": [os.path.basename(path)] if exists else [],
        "error": None if exists else f"Model file not found at: {path}"
    }
