# Smart Defence Decision Systems (SDDS)

SDDS is a 100% offline, air-gapped, CPU-optimized Command and Control (C2) tactical intelligence interface where an AI tactical assistant (**ATLAS**) can bidirectionally read from and write to a live operational map in real-time.

Designed for operational deployment on standard laptops without GPU hardware or external internet access, it runs entirely locally with no external APIs.

---

## Technical Features

- **Frontend**: Full-screen OpenLayers tactical map utilizing CartoDB Dark Matter map tiles cached locally/remotely. Uses a left-sliding drawer for C2 communication, a custom status bar, and real-time cursor coordinate feedback. Built in pure HTML, CSS, and Javascript for auditability, high performance, and security compliance.
- **Backend**: FastAPI Python backend exposing asynchronous endpoints for C2 execution.
- **Local Inference**: Powered by `llama-cpp-python` running a 4-bit quantized **Qwen2.5-3B-Instruct** GGUF model (~2.2 GB) entirely on CPU. It features prompt-caching, low memory overhead, and strict JSON schema output compliance.
- **Utilitarian Aesthetics**: Everforest dark theme, JetBrains Mono font, zero border-radius (hard edges), and tactical color-coded map overlays (pins, polygons, paths, and labels).

---

## Setup & Startup Instructions

### Prerequisites
1. **Python**: Python 3.11 or later.
2. **uv**: Astral's high-performance Python package manager. If you don't have it, install it using:
   ```cmd
   winget install astral-sh.uv
   ```

### Quick Start (One-Click Launch)
Simply run the included **`start.bat`** script:
1. Double-click `start.bat` (or run it via Command Prompt).
2. If this is the first run, the script will detect that the model file is missing and prompt you to download it:
   ```
   [!]  Local GGUF model file not found.
   Would you like to download the recommended model now? [Y,N]
   ```
3. Press **`Y`** to launch the downloader script (`download_model.bat`), which downloads the official **Qwen2.5-3B-Instruct** GGUF model directly from Hugging Face with a visual progress bar.
4. Once completed, `start.bat` will automatically:
   - Synchronize all dependencies inside a local virtual environment.
   - Start the FastAPI backend server on port `8000`.
   - Start the local HTTP frontend server on port `3000`.
   - Open your browser to the C2 dashboard: `http://localhost:3000`

---

## C2 Command Protocol (Interactive Map Commands)

ATLAS is equipped with an integrated operational database representing a tactical sector. When you send queries in the sliding chat drawer, ATLAS responds in structured JSON, mapping visual indicators directly to the map:
- **Drop Pin**: Marks a point of interest or friendly/hostile unit.
- **Highlight Zone**: Colors a whole tactical region (e.g., safe base, observation post, hostile camping area).
- **Highlight Road**: Traces a specific pre-defined Main Supply Route (MSR) from coordinates database.
- **Trace Path**: Visualizes custom patrol paths or tactical maneuvers on the map.
- **Fit to Zone**: Focuses and pans the map camera directly to the relevant operational sector.
- **Add Label**: Marks coordinates with tactical annotations.

### Sample Operational Commands
Try typing these into the C2 drawer:
* *"Where are the op camping zones? Pan the map to show them."*
* *"What is the best path to reach BRAVO camp from the friendly ALPHA base?"*
* *"I clicked on coordinates [75.52, 34.08]. What is near this location? Drop a pin there."*
* *"Clear the overlays."*

---

## Directory Architecture

```
SDDS/
├── backend/
│   ├── main.py                  # FastAPI server and routing
│   ├── llama_cpp_client.py      # Local CPU-optimized LLM runner
│   ├── map_data.py              # Operational coordinate database (zones, routes, landmarks)
│   ├── pyproject.toml           # Backend project description and dependencies
│   └── requirements.txt         # Text requirements file
├── frontend/
│   ├── index.html               # Main tactile C2 web dashboard
│   ├── style.css                # Everforest-dark styling system (utilitarian layout)
│   └── app.js                   # OpenLayers maps client and commands executor
├── models/
│   └── qwen2.5-3b-instruct-...  # Local GGUF model binary (~2.0 GB, auto-downloaded)
├── start.bat                    # One-click startup launcher script
├── download_model.bat           # Downloader invoking batch script
└── download_model.py            # Python model downloader with progress tracking
```

---

## Advanced Configurations

### Custom Model Paths
If you already have a GGUF model on your system, you can direct SDDS to use it by setting the `SDDS_MODEL_PATH` environment variable:
```cmd
set SDDS_MODEL_PATH=C:\path\to\your\model.gguf
start.bat
```
This is fully compatible with any modern Llama, Phi, Gemma, or Qwen GGUF model with standard instruction-tuning!
