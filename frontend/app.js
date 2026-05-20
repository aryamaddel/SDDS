// ═══════════════════════════════════════════════════════════════════════════
// SDDS — app.js
// OpenLayers map + ATLAS chat interface + map command executor
// ═══════════════════════════════════════════════════════════════════════════

const API = "http://localhost:8000";

// Everforest colour palette (mirrors CSS vars)
const C = {
  green:  "#a7c080",
  amber:  "#e69875",
  red:    "#e67e80",
  cyan:   "#83c092",
  blue:   "#7fbbb3",
  yellow: "#dbbc7f",
  white:  "#d3c6aa",
  dim:    "#4a555b",
};

function color(name) { return C[name] ?? C.white; }

// Tactical data cached after first fetch (used by highlight_road)
let tacticalCache = null;

// ═══════════════════════════════════════════════════════════════════════════
// MAP INITIALISATION
// ═══════════════════════════════════════════════════════════════════════════

// Base tile sources (OpenStreetMap standard, Voyager, and Dark Matter)
const themeSources = {
  dark: "https://{a-c}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png",
  voyager: "https://{a-c}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png",
  light: "https://tile.openstreetmap.org/{z}/{x}/{y}.png", // OpenStreetMap: Ultra-high visibility, clear borders, roads, forests, and contours!
};

let currentTheme = "light";

// Base tile layer — Defaults to OpenStreetMap Light (no API key needed)
const tileLayer = new ol.layer.Tile({
  source: new ol.source.XYZ({
    url: themeSources.light,
    attributions:
      '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
    maxZoom: 19,
  }),
});

// Permanent base tactical layer (dim zones / routes loaded from backend)
const baseSource = new ol.source.Vector();
const baseLayer  = new ol.layer.Vector({ source: baseSource, zIndex: 5 });

// AI-driven overlay layers (manipulated by map commands)
const src = {
  zones: new ol.source.Vector(),
  paths: new ol.source.Vector(),
  pins:  new ol.source.Vector(),
  labels: new ol.source.Vector(),
};
const aiLayers = {
  zones:  new ol.layer.Vector({ source: src.zones,  zIndex: 10 }),
  paths:  new ol.layer.Vector({ source: src.paths,  zIndex: 15 }),
  pins:   new ol.layer.Vector({ source: src.pins,   zIndex: 20 }),
  labels: new ol.layer.Vector({ source: src.labels, zIndex: 25 }),
};

const map = new ol.Map({
  target: "map",
  layers: [
    tileLayer,
    baseLayer,
    aiLayers.zones,
    aiLayers.paths,
    aiLayers.pins,
    aiLayers.labels,
  ],
  view: new ol.View({
    center: ol.proj.fromLonLat([75.5, 34.0]),
    zoom: 12,
    minZoom: 8,
    maxZoom: 18,
  }),
  controls: ol.control.defaults.defaults({ zoom: false, rotate: false }),
});


// ═══════════════════════════════════════════════════════════════════════════
// STYLE HELPERS
// ═══════════════════════════════════════════════════════════════════════════

function hexToRgba(hex, alpha) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return `rgba(${r},${g},${b},${alpha})`;
}

function pinStyle(colorName, label) {
  const c = color(colorName);
  return new ol.style.Style({
    image: new ol.style.RegularShape({
      points: 4,
      radius: 9,
      radius2: 4,
      angle: 0,
      fill: new ol.style.Fill({ color: c }),
      stroke: new ol.style.Stroke({ color: "#1a2126", width: 1 }),
    }),
    text: label
      ? new ol.style.Text({
          text: label,
          font: "600 10px 'JetBrains Mono', monospace",
          fill: new ol.style.Fill({ color: c }),
          stroke: new ol.style.Stroke({ color: "#1a2126", width: 3 }),
          offsetY: -20,
          textAlign: "center",
        })
      : undefined,
  });
}

function zoneStyle(colorName, label, opacity = 0.35) {
  const c = color(colorName);
  return new ol.style.Style({
    fill: new ol.style.Fill({ color: hexToRgba(c, opacity) }),
    stroke: new ol.style.Stroke({ color: c, width: 1.5 }),
    text: label
      ? new ol.style.Text({
          text: label,
          font: "600 11px 'JetBrains Mono', monospace",
          fill: new ol.style.Fill({ color: c }),
          stroke: new ol.style.Stroke({ color: "#1a2126", width: 3 }),
        })
      : undefined,
  });
}

function pathStyle(colorName, label, width = 3) {
  const c = color(colorName);
  const styles = [
    new ol.style.Style({
      stroke: new ol.style.Stroke({ color: c, width, lineDash: [10, 5] }),
    }),
  ];
  if (label) {
    styles.push(
      new ol.style.Style({
        text: new ol.style.Text({
          text: label,
          font: "500 10px 'JetBrains Mono', monospace",
          fill: new ol.style.Fill({ color: c }),
          stroke: new ol.style.Stroke({ color: "#1a2126", width: 3 }),
          placement: "line",
          overflow: true,
        }),
      })
    );
  }
  return styles;
}

function labelStyle(text, colorName) {
  const c = color(colorName);
  return new ol.style.Style({
    text: new ol.style.Text({
      text,
      font: "600 11px 'JetBrains Mono', monospace",
      fill: new ol.style.Fill({ color: c }),
      stroke: new ol.style.Stroke({ color: "#1a2126", width: 3 }),
    }),
  });
}

// Dim styles for the permanent base layer (adapts to light/dark themes dynamically)
function dimZoneStyle(colorName) {
  const c = color(colorName);
  const isLight = currentTheme === "light";
  return new ol.style.Style({
    fill: new ol.style.Fill({ color: hexToRgba(c, isLight ? 0.08 : 0.04) }),
    stroke: new ol.style.Stroke({ color: hexToRgba(c, isLight ? 0.45 : 0.28), width: isLight ? 1.8 : 1 }),
  });
}

function dimLineStyle(colorName, alpha = 0.2) {
  const isLight = currentTheme === "light";
  const adjustedAlpha = isLight ? Math.min(alpha * 2.2, 0.7) : alpha;
  const adjustedWidth = isLight ? 2.2 : 1.5;
  return new ol.style.Style({
    stroke: new ol.style.Stroke({ color: hexToRgba(color(colorName), adjustedAlpha), width: adjustedWidth }),
  });
}


// ═══════════════════════════════════════════════════════════════════════════
// BASE TACTICAL DATA LOADER
// Draws permanent dim outlines so the AO context is always visible
// ═══════════════════════════════════════════════════════════════════════════

async function loadTacticalData() {
  try {
    const res = await fetch(`${API}/api/map-data`);
    if (!res.ok) return;
    const data = await res.json();
    tacticalCache = data;

    // Zones — dim outlines + name labels
    for (const zone of Object.values(data.zones)) {
      const poly = new ol.geom.Polygon([
        zone.polygon.map((c) => ol.proj.fromLonLat(c)),
      ]);
      const feat = new ol.Feature({ geometry: poly });
      feat.setStyle(() => dimZoneStyle(zone.color));
      baseSource.addFeature(feat);

      // Zone label centred on polygon
      const label = new ol.Feature({
        geometry: new ol.geom.Point(ol.proj.fromLonLat(zone.center)),
      });
      label.setStyle(() => {
        const isLight = currentTheme === "light";
        return new ol.style.Style({
          text: new ol.style.Text({
            text: zone.name,
            font: "500 9px 'JetBrains Mono', monospace",
            fill: new ol.style.Fill({ color: hexToRgba(color(zone.color), isLight ? 0.85 : 0.45) }),
            stroke: new ol.style.Stroke({ color: isLight ? "#ffffff" : "#1a2126", width: 2 }),
          }),
        });
      });
      baseSource.addFeature(label);
    }

    // Routes — dim dashed lines
    for (const route of Object.values(data.routes)) {
      const line = new ol.Feature({
        geometry: new ol.geom.LineString(
          route.coords.map((c) => ol.proj.fromLonLat(c))
        ),
      });
      line.setStyle(() => dimLineStyle(route.color));
      baseSource.addFeature(line);
    }

    // River — bluish dim line
    for (const lm of data.landmarks) {
      if (Array.isArray(lm.coords[0])) {
        const river = new ol.Feature({
          geometry: new ol.geom.LineString(
            lm.coords.map((c) => ol.proj.fromLonLat(c))
          ),
        });
        river.setStyle(() => dimLineStyle("cyan", 0.14));
        baseSource.addFeature(river);
      } else {
        // Point landmark — tiny dot
        const dot = new ol.Feature({
          geometry: new ol.geom.Point(ol.proj.fromLonLat(lm.coords)),
        });
        dot.setStyle(() => {
          const isLight = currentTheme === "light";
          return new ol.style.Style({
            image: new ol.style.Circle({
              radius: isLight ? 4 : 3,
              fill: new ol.style.Fill({ color: hexToRgba(C.amber, isLight ? 0.75 : 0.4) }),
            }),
          });
        });
        baseSource.addFeature(dot);
      }
    }
  } catch (err) {
    console.warn("Could not load tactical data:", err);
  }
}


// ═══════════════════════════════════════════════════════════════════════════
// MAP COMMAND EXECUTOR
// Receives the map_commands array from the backend and applies each command
// ═══════════════════════════════════════════════════════════════════════════

function execCommands(commands) {
  if (!Array.isArray(commands)) return;
  for (const cmd of commands) {
    try {
      switch (cmd.type) {
        case "drop_pin":       execDropPin(cmd);       break;
        case "highlight_zone": execHighlightZone(cmd); break;
        case "highlight_road": execHighlightRoad(cmd); break;
        case "trace_path":     execTracePath(cmd);     break;
        case "clear_layer":    execClearLayer(cmd);    break;
        case "fit_to_zone":    execFitToZone(cmd);     break;
        case "add_label":      execAddLabel(cmd);      break;
        default: console.warn("SDDS: unknown map command →", cmd.type);
      }
    } catch (e) {
      console.error("SDDS: error executing command", cmd, e);
    }
  }
}

// ── Helpers ──

function removeById(source, id) {
  if (!id) return;
  const existing = source.getFeatures().find((f) => f.get("fid") === id);
  if (existing) source.removeFeature(existing);
}

function lonLatToMap(c) { return ol.proj.fromLonLat(c); }

// ── Command implementations ──

function execDropPin({ id, coords, label, color: col = "amber" }) {
  if (!coords) return;
  removeById(src.pins, id);
  const f = new ol.Feature({ geometry: new ol.geom.Point(lonLatToMap(coords)), fid: id });
  f.setStyle(pinStyle(col, label));
  src.pins.addFeature(f);
}

function execHighlightZone({ id, coords, color: col = "green", label, opacity = 0.35 }) {
  if (!coords?.length) return;
  removeById(src.zones, id);
  const f = new ol.Feature({
    geometry: new ol.geom.Polygon([coords.map(lonLatToMap)]),
    fid: id,
  });
  f.setStyle(zoneStyle(col, label, opacity));
  src.zones.addFeature(f);
}

function execHighlightRoad({ id, route_id, color: col = "amber", width = 3, label }) {
  // Look up route coordinates by ID from cached tactical data
  const route = tacticalCache?.routes?.[route_id];
  if (!route) {
    console.warn("SDDS: unknown route_id →", route_id);
    return;
  }
  execTracePath({
    id: id ?? `road_${route_id}`,
    coords: route.coords,
    color: col,
    label: label ?? route.name,
    width,
  });
}

function execTracePath({ id, coords, color: col = "cyan", label, width = 3 }) {
  if (!coords?.length) return;
  removeById(src.paths, id);
  const f = new ol.Feature({
    geometry: new ol.geom.LineString(coords.map(lonLatToMap)),
    fid: id,
  });
  f.setStyle(pathStyle(col, label, width));
  src.paths.addFeature(f);
}

function execClearLayer({ layer }) {
  if (layer === "all") {
    Object.values(src).forEach((s) => s.clear());
  } else if (src[layer]) {
    src[layer].clear();
  }
}

function execFitToZone({ coords }) {
  if (!coords?.length) return;
  const extent = ol.extent.createEmpty();
  coords.forEach((c) => {
    const pt = lonLatToMap(c);
    ol.extent.extend(extent, [pt[0], pt[1], pt[0], pt[1]]);
  });
  map.getView().fit(extent, { padding: [80, 80, 80, 80], duration: 700, maxZoom: 14 });
}

function execAddLabel({ id, coords, text, color: col = "white" }) {
  if (!coords || !text) return;
  removeById(src.labels, id);
  const f = new ol.Feature({
    geometry: new ol.geom.Point(lonLatToMap(coords)),
    fid: id,
  });
  f.setStyle(labelStyle(text, col));
  src.labels.addFeature(f);
}


// ═══════════════════════════════════════════════════════════════════════════
// MAP CONTEXT BUILDER
// Packages up current map state to send to the LLM
// ═══════════════════════════════════════════════════════════════════════════

function buildMapContext() {
  const view   = map.getView();
  const center = ol.proj.toLonLat(view.getCenter()).map((v) => +v.toFixed(5));
  const zoom   = +view.getZoom().toFixed(1);
  const ext    = view.calculateExtent(map.getSize());
  const sw     = ol.proj.toLonLat([ext[0], ext[1]]).map((v) => +v.toFixed(5));
  const ne     = ol.proj.toLonLat([ext[2], ext[3]]).map((v) => +v.toFixed(5));

  const overlays = [];
  Object.entries(src).forEach(([layer, source]) => {
    source.getFeatures().forEach((f) => {
      const fid = f.get("fid");
      if (fid) overlays.push({ layer, id: fid });
    });
  });

  return { center, zoom, bbox: { sw, ne }, active_overlays: overlays };
}


// ═══════════════════════════════════════════════════════════════════════════
// CHAT INTERFACE
// ═══════════════════════════════════════════════════════════════════════════

const $log    = document.getElementById("chat-messages");
const $input  = document.getElementById("chat-input");
const $send   = document.getElementById("send-btn");
const $drawer = document.getElementById("drawer");

let thinking = false;

function appendMsg(role, text, cmdCount = 0) {
  const wrap = document.createElement("div");
  wrap.className = `msg ${role}-msg`;

  const tag = document.createElement("span");
  tag.className = "msg-tag";
  tag.textContent =
    role === "user"   ? "[OPR]"    :
    role === "atlas"  ? "[ATLAS]"  :
    role === "error"  ? "[ERR]"    : "[SYS]";

  const body = document.createElement("span");
  body.className = "msg-text";
  body.textContent = text;

  wrap.appendChild(tag);
  wrap.appendChild(body);

  if (cmdCount > 0) {
    const badge = document.createElement("span");
    badge.className = "map-cmd-badge";
    badge.textContent = `↑ ${cmdCount} map update${cmdCount !== 1 ? "s" : ""} applied`;
    wrap.appendChild(badge);
  }

  $log.appendChild(wrap);
  $log.scrollTop = $log.scrollHeight;
  return wrap;
}

function appendThinking() {
  const wrap = document.createElement("div");
  wrap.className = "msg atlas-msg thinking-msg";

  const tag = document.createElement("span");
  tag.className = "msg-tag";
  tag.textContent = "[ATLAS]";

  const body = document.createElement("span");
  body.className = "msg-text";

  const dots = document.createElement("span");
  dots.className = "thinking-dots";
  dots.textContent = "Processing";

  body.appendChild(dots);
  wrap.appendChild(tag);
  wrap.appendChild(body);
  $log.appendChild(wrap);
  $log.scrollTop = $log.scrollHeight;
  return wrap;
}

async function sendChat(message) {
  message = message.trim();
  if (!message || thinking) return;

  thinking = true;
  $send.disabled = true;
  $input.value = "";

  appendMsg("user", message);
  const thinkEl = appendThinking();
  setStatus("thinking");

  try {
    const res = await fetch(`${API}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, map_context: buildMapContext() }),
    });

    if (!res.ok) throw new Error(`HTTP ${res.status}`);

    const data = await res.json();
    thinkEl.remove();

    execCommands(data.map_commands);
    appendMsg("atlas", data.message, data.map_commands?.length ?? 0);
    setStatus("online");
  } catch (err) {
    thinkEl.remove();
    appendMsg("error", `Transmission failed: ${err.message}`);
    setStatus("offline");
  } finally {
    thinking = false;
    $send.disabled = false;
    $input.focus();
  }
}


// ═══════════════════════════════════════════════════════════════════════════
// STATUS BAR
// ═══════════════════════════════════════════════════════════════════════════

const $aiStatus  = document.getElementById("ai-status");
const $modelName = document.getElementById("model-name");

function setStatus(state) {
  $aiStatus.className = "";
  if (state === "online") {
    $aiStatus.className = "status-online";
    $aiStatus.textContent = "● ONLINE";
  } else if (state === "offline") {
    $aiStatus.className = "status-offline";
    $aiStatus.textContent = "● OFFLINE";
  } else {
    $aiStatus.className = "status-thinking";
    $aiStatus.textContent = "◌ PROCESSING";
  }
}

async function checkHealth() {
  try {
    const res = await fetch(`${API}/health`, {
      signal: AbortSignal.timeout(3000),
    });
    if (!res.ok) throw new Error();
    const data = await res.json();
    if (data.ollama?.online) {
      setStatus("online");
      if (data.model) $modelName.textContent = data.model;
    } else {
      setStatus("offline");
      $modelName.textContent = "";
    }
  } catch {
    setStatus("offline");
    $modelName.textContent = "";
  }
}


// ═══════════════════════════════════════════════════════════════════════════
// UI EVENT BINDINGS
// ═══════════════════════════════════════════════════════════════════════════

// ── Drawer toggle ──
const $toggle = document.getElementById("drawer-toggle");
const $arrow  = document.getElementById("toggle-icon");

$toggle.addEventListener("click", () => {
  const open = $drawer.classList.toggle("open");
  $arrow.textContent = open ? "◀" : "▶";
});

// ── Send button ──
$send.addEventListener("click", () => sendChat($input.value));

// ── Ctrl+Enter to send ──
$input.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && e.ctrlKey) {
    e.preventDefault();
    sendChat($input.value);
  }
});

// ── Quick-query chips ──
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    const query = chip.dataset.query;
    if (!query) return;
    // Open drawer if closed
    if (!$drawer.classList.contains("open")) {
      $drawer.classList.add("open");
      $arrow.textContent = "◀";
    }
    sendChat(query);
  });
});

// ── Clear chat log ──
document.getElementById("clear-chat").addEventListener("click", () => {
  $log.innerHTML = "";
  appendMsg("system", "Log cleared. ATLAS ready.");
});

// ── Map controls ──
document.getElementById("btn-clear-all").addEventListener("click", () => {
  Object.values(src).forEach((s) => s.clear());
  appendMsg("system", "All AI overlays cleared.");
});

document.getElementById("btn-reset-view").addEventListener("click", () => {
  map.getView().animate({
    center: ol.proj.fromLonLat([75.5, 34.0]),
    zoom: 12,
    duration: 600,
  });
});

let baseVisible = true;
document.getElementById("btn-toggle-base").addEventListener("click", function () {
  baseVisible = !baseVisible;
  baseLayer.setVisible(baseVisible);
  this.classList.toggle("active", !baseVisible);
});

// ── Theme Switchers ──
function setMapTheme(theme) {
  if (!themeSources[theme]) return;
  currentTheme = theme;

  tileLayer.setSource(
    new ol.source.XYZ({
      url: themeSources[theme],
      attributions:
        '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors ' +
        '© <a href="https://carto.com/attributions">CARTO</a>',
      maxZoom: 19,
    })
  );

  // Update active state in UI
  document.querySelectorAll(".theme-btn").forEach((btn) => {
    btn.classList.toggle("active", btn.id === `theme-${theme}`);
  });

  // Force redraw of base source and other features to apply adaptive styles
  baseSource.changed();
  Object.values(src).forEach((s) => s.changed());
}

document.getElementById("theme-dark").addEventListener("click", () => setMapTheme("dark"));
document.getElementById("theme-voyager").addEventListener("click", () => setMapTheme("voyager"));
document.getElementById("theme-light").addEventListener("click", () => setMapTheme("light"));

// ── Coordinate display on pointer move ──
const $coords = document.getElementById("coord-display");
map.on("pointermove", (e) => {
  if (e.dragging) return;
  const [lon, lat] = ol.proj.toLonLat(e.coordinate);
  const ns = lat >= 0 ? "N" : "S";
  const ew = lon >= 0 ? "E" : "W";
  $coords.textContent =
    `${Math.abs(lat).toFixed(4)}°${ns}  ${Math.abs(lon).toFixed(4)}°${ew}`;
});

// ── Click → coord popup ──
const $popup      = document.getElementById("click-popup");
const $popupCoord = document.getElementById("click-coords-text");
const $popupBtn   = document.getElementById("click-query-btn");
let clickedLonLat = null;
let popupTimer    = null;

map.on("click", (e) => {
  const [lon, lat] = ol.proj.toLonLat(e.coordinate);
  clickedLonLat = [+lon.toFixed(5), +lat.toFixed(5)];
  $popupCoord.textContent = `${clickedLonLat[1]}°N  ${clickedLonLat[0]}°E`;
  $popup.style.display = "flex";
  clearTimeout(popupTimer);
  popupTimer = setTimeout(() => ($popup.style.display = "none"), 5000);
});

$popupBtn.addEventListener("click", () => {
  if (!clickedLonLat) return;
  const q = `I clicked on coordinates [${clickedLonLat[0]}, ${clickedLonLat[1]}]. What is at or near this location? Give me a tactical assessment and drop a pin there.`;
  $popup.style.display = "none";
  if (!$drawer.classList.contains("open")) {
    $drawer.classList.add("open");
    $arrow.textContent = "◀";
  }
  sendChat(q);
});


// ═══════════════════════════════════════════════════════════════════════════
// BOOT
// ═══════════════════════════════════════════════════════════════════════════

async function boot() {
  // Open drawer by default
  $drawer.classList.add("open");
  $arrow.textContent = "◀";

  // Load permanent base layer
  await loadTacticalData();

  // Check backend health
  await checkHealth();

  // Poll health every 12 seconds
  setInterval(checkHealth, 12_000);
}

boot();
