"""
ADAS QA Viewer Generator
========================
Reads camera frames + fused/lidar JSON annotations,
encodes everything into a single self-contained HTML file.

Expected input structure:
  outputs/frames/front_wide/       -> frame_0.jpg, frame_1.jpg, ...
  outputs/fused_detections/fused.json
  outputs/lidar_annotations/lidar.json

Output:
  adas_viewer.html
"""

import os
import json
import base64

# ── Paths ────────────────────────────────────────────────────────────────────
FRAME_DIR   = "outputs/camera_detections/front_wide"
FUSED_FILE  = "outputs/fused_detections/frame_000.json"
LIDAR_FILE  = "outputs/lidar_annotations/frame_000.json"
OUTPUT_HTML = "adas_viewer.html"


def encode_image(path: str) -> str:
    """Return base64-encoded string of an image file."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


# ── Load annotation data ─────────────────────────────────────────────────────
print("Loading detections...")

with open(FUSED_FILE, "r") as f:
    fused_data = json.load(f)

with open(LIDAR_FILE, "r") as f:
    lidar_data = json.load(f)

# ── Encode frames ─────────────────────────────────────────────────────────────
print("Encoding frames...")

frames: dict[int, str] = {}

for file in sorted(os.listdir(FRAME_DIR)):
    if not file.endswith(".jpg"):
        continue

    # Extract frame number from filename like "frame_0.jpg"
    try:
        frame_index = int(file.split("_")[1].split(".")[0])
    except (IndexError, ValueError):
        continue

    img_path = os.path.join(FRAME_DIR, file)
    frames[frame_index] = encode_image(img_path)

if not frames:
    raise RuntimeError(f"No frames found in {FRAME_DIR}")

max_frame = max(frames.keys())
print(f"  → {len(frames)} frames encoded (0–{max_frame})")

# ── Generate HTML ─────────────────────────────────────────────────────────────
print("Generating HTML...")

html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ADAS QA Viewer · Qualcomm</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Barlow+Condensed:wght@300;400;600;700&display=swap" rel="stylesheet">
<style>
  /* ── Reset & base ── */
  *, *::before, *::after {{ box-sizing: border-box; margin: 0; padding: 0; }}

  :root {{
    --bg:        #060b12;
    --surface:   #0c1520;
    --surface2:  #0f1d2b;
    --border:    #1a3045;
    --cyan:      #00d4ff;
    --cyan-dim:  #006a80;
    --green:     #00ff9d;
    --amber:     #ffb300;
    --red:       #ff4444;
    --text:      #b8d4e8;
    --text-dim:  #4a6a84;
    --mono:      'Share Tech Mono', monospace;
    --display:   'Barlow Condensed', sans-serif;
  }}

  html, body {{
    background: var(--bg);
    color: var(--text);
    font-family: var(--mono);
    height: 100%;
    overflow-x: hidden;
  }}

  /* Scanline texture overlay */
  body::before {{
    content: '';
    position: fixed; inset: 0;
    background: repeating-linear-gradient(
      0deg,
      transparent,
      transparent 2px,
      rgba(0,0,0,0.18) 2px,
      rgba(0,0,0,0.18) 4px
    );
    pointer-events: none;
    z-index: 9999;
  }}

  /* ── Layout ── */
  .shell {{
    max-width: 1440px;
    margin: 0 auto;
    padding: 0 24px 40px;
  }}

  /* ── Header ── */
  header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 18px 0 14px;
    border-bottom: 1px solid var(--border);
    animation: fadeDown 0.5s ease both;
  }}
  .logo-group {{
    display: flex;
    align-items: center;
    gap: 14px;
  }}
  .logo-pip {{
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--cyan);
    box-shadow: 0 0 12px var(--cyan), 0 0 30px rgba(0,212,255,0.4);
    animation: pulse 2s ease-in-out infinite;
  }}
  @keyframes pulse {{
    0%, 100% {{ opacity: 1; transform: scale(1); }}
    50%       {{ opacity: 0.5; transform: scale(0.7); }}
  }}
  .logo-text {{
    font-family: var(--display);
    font-weight: 700;
    font-size: 22px;
    letter-spacing: 3px;
    color: #fff;
    text-transform: uppercase;
  }}
  .logo-sub {{
    font-size: 11px;
    color: var(--text-dim);
    letter-spacing: 2px;
    margin-top: 2px;
  }}
  .header-badges {{
    display: flex;
    gap: 10px;
    align-items: center;
  }}
  .badge {{
    font-size: 10px;
    font-family: var(--mono);
    letter-spacing: 1.5px;
    padding: 4px 10px;
    border-radius: 2px;
    border: 1px solid var(--border);
    color: var(--text-dim);
  }}
  .badge.live {{
    border-color: var(--green);
    color: var(--green);
  }}

  /* ── Status bar ── */
  .statusbar {{
    display: flex;
    gap: 32px;
    padding: 10px 0;
    border-bottom: 1px solid var(--border);
    font-size: 11px;
    color: var(--text-dim);
    letter-spacing: 1px;
    animation: fadeDown 0.5s 0.1s ease both;
  }}
  .stat-item {{ display: flex; flex-direction: column; gap: 2px; }}
  .stat-label {{ font-size: 9px; letter-spacing: 2px; text-transform: uppercase; }}
  .stat-val {{ color: var(--cyan); font-size: 14px; }}

  /* ── Main panels ── */
  .panels {{
    display: grid;
    grid-template-columns: 1fr 380px;
    gap: 16px;
    margin-top: 16px;
    animation: fadeUp 0.5s 0.2s ease both;
  }}

  .panel {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    overflow: hidden;
    position: relative;
  }}
  .panel::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--cyan), transparent);
    opacity: 0.5;
  }}

  .panel-header {{
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    background: var(--surface2);
  }}
  .panel-title {{
    font-family: var(--display);
    font-weight: 600;
    font-size: 13px;
    letter-spacing: 3px;
    color: var(--cyan);
    text-transform: uppercase;
  }}
  .panel-meta {{
    font-size: 10px;
    color: var(--text-dim);
    letter-spacing: 1px;
  }}

  .panel-body {{
    padding: 0;
    position: relative;
    background: #000;
  }}

  /* Camera canvas */
  #cameraCanvas {{
    display: block;
    width: 100%;
    height: auto;
    max-height: 520px;
    object-fit: contain;
  }}

  /* LiDAR canvas */
  #lidarCanvas {{
    display: block;
    width: 100%;
    height: 380px;
    background: radial-gradient(ellipse at center, #071120 0%, #030810 100%);
  }}

  /* Overlay for "no data" */
  .no-data {{
    position: absolute; inset: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; color: var(--text-dim); letter-spacing: 2px;
  }}

  /* ── Bottom: scrubber + detections ── */
  .bottom {{
    display: grid;
    grid-template-columns: 1fr 380px;
    gap: 16px;
    margin-top: 16px;
    animation: fadeUp 0.5s 0.3s ease both;
  }}

  /* Scrubber panel */
  .scrubber-panel {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 16px 20px;
  }}
  .scrubber-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
  }}
  .scrubber-label {{
    font-size: 10px;
    letter-spacing: 2px;
    color: var(--text-dim);
    text-transform: uppercase;
  }}
  .frame-display {{
    font-size: 28px;
    color: var(--cyan);
    letter-spacing: -1px;
    line-height: 1;
  }}
  .frame-total {{
    font-size: 11px;
    color: var(--text-dim);
  }}

  /* Custom range input */
  input[type=range] {{
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 4px;
    background: var(--border);
    border-radius: 2px;
    outline: none;
    cursor: pointer;
    margin: 8px 0;
  }}
  input[type=range]::-webkit-slider-thumb {{
    -webkit-appearance: none;
    width: 16px; height: 16px;
    border-radius: 50%;
    background: var(--cyan);
    box-shadow: 0 0 10px var(--cyan);
    cursor: pointer;
    transition: transform 0.1s;
  }}
  input[type=range]::-webkit-slider-thumb:active {{
    transform: scale(1.3);
  }}
  input[type=range]::-webkit-slider-runnable-track {{
    height: 4px;
    border-radius: 2px;
  }}

  /* Playback controls */
  .controls {{
    display: flex;
    gap: 8px;
    margin-top: 10px;
    align-items: center;
  }}
  .ctrl-btn {{
    background: var(--surface2);
    border: 1px solid var(--border);
    color: var(--text);
    font-family: var(--mono);
    font-size: 11px;
    letter-spacing: 1px;
    padding: 6px 14px;
    border-radius: 2px;
    cursor: pointer;
    transition: all 0.15s;
  }}
  .ctrl-btn:hover {{ background: var(--border); color: var(--cyan); border-color: var(--cyan); }}
  .ctrl-btn.active {{ background: var(--cyan-dim); border-color: var(--cyan); color: var(--cyan); }}

  .fps-label {{
    font-size: 10px;
    color: var(--text-dim);
    margin-left: auto;
    letter-spacing: 1px;
  }}

  /* Detection list panel */
  .det-panel {{
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 4px;
    overflow: hidden;
  }}
  .det-header {{
    padding: 10px 14px;
    border-bottom: 1px solid var(--border);
    background: var(--surface2);
    font-family: var(--display);
    font-weight: 600;
    font-size: 13px;
    letter-spacing: 3px;
    color: var(--amber);
    text-transform: uppercase;
  }}
  .det-list {{
    max-height: 148px;
    overflow-y: auto;
    padding: 6px 0;
  }}
  .det-list::-webkit-scrollbar {{ width: 4px; }}
  .det-list::-webkit-scrollbar-track {{ background: var(--surface); }}
  .det-list::-webkit-scrollbar-thumb {{ background: var(--border); border-radius: 2px; }}

  .det-item {{
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 5px 14px;
    font-size: 11px;
    border-bottom: 1px solid transparent;
    transition: background 0.1s;
  }}
  .det-item:hover {{ background: var(--surface2); }}
  .det-dot {{
    width: 6px; height: 6px;
    border-radius: 50%;
    flex-shrink: 0;
  }}
  .det-class {{
    color: #fff;
    letter-spacing: 1px;
    min-width: 90px;
    font-family: var(--display);
    font-weight: 600;
    font-size: 12px;
  }}
  .det-conf {{
    color: var(--text-dim);
    font-size: 10px;
    margin-left: auto;
    letter-spacing: 1px;
  }}
  .det-pos {{
    color: var(--text-dim);
    font-size: 10px;
    letter-spacing: 0.5px;
  }}
  .det-empty {{
    padding: 20px;
    text-align: center;
    font-size: 11px;
    color: var(--text-dim);
    letter-spacing: 2px;
  }}

  /* ── Keyframes ── */
  @keyframes fadeDown {{
    from {{ opacity: 0; transform: translateY(-10px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}
  @keyframes fadeUp {{
    from {{ opacity: 0; transform: translateY(12px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
  }}
  @keyframes radarSweep {{
    from {{ transform: rotate(0deg); }}
    to   {{ transform: rotate(360deg); }}
  }}
</style>
</head>
<body>
<div class="shell">

  <!-- Header -->
  <header>
    <div class="logo-group">
      <div class="logo-pip"></div>
      <div>
        <div class="logo-text">ADAS QA Viewer</div>
        <div class="logo-sub">SENSOR FUSION · QUALCOMM POC</div>
      </div>
    </div>
    <div class="header-badges">
      <div class="badge live">● LIVE REPLAY</div>
      <div class="badge">SESSION_001</div>
      <div class="badge">FRONT_WIDE</div>
    </div>
  </header>

  <!-- Status bar -->
  <div class="statusbar">
    <div class="stat-item">
      <span class="stat-label">Total Frames</span>
      <span class="stat-val" id="statTotal">{max_frame + 1}</span>
    </div>
    <div class="stat-item">
      <span class="stat-label">Current Frame</span>
      <span class="stat-val" id="statFrame">0</span>
    </div>
    <div class="stat-item">
      <span class="stat-label">Objects</span>
      <span class="stat-val" id="statObjects">—</span>
    </div>
    <div class="stat-item">
      <span class="stat-label">LiDAR Pts</span>
      <span class="stat-val" id="statLidar">—</span>
    </div>
    <div class="stat-item">
      <span class="stat-label">Sensor</span>
      <span class="stat-val" style="color:var(--green)">FUSED</span>
    </div>
  </div>

  <!-- Main panels -->
  <div class="panels">

    <!-- Camera panel -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">Camera · 2D Detection</span>
        <span class="panel-meta" id="camMeta">1280 × 720</span>
      </div>
      <div class="panel-body">
        <canvas id="cameraCanvas"></canvas>
        <div class="no-data" id="camNoData" style="display:none">NO FRAME DATA</div>
      </div>
    </div>

    <!-- LiDAR panel -->
    <div class="panel">
      <div class="panel-header">
        <span class="panel-title">LiDAR · Bird's Eye</span>
        <span class="panel-meta">TOP-DOWN VIEW</span>
      </div>
      <div class="panel-body">
        <canvas id="lidarCanvas" width="380" height="380"></canvas>
      </div>
    </div>

  </div><!-- /panels -->

  <!-- Bottom row -->
  <div class="bottom">

    <!-- Scrubber -->
    <div class="scrubber-panel">
      <div class="scrubber-top">
        <div>
          <div class="scrubber-label">Frame Index</div>
          <div class="frame-display" id="frameDisplay">0000</div>
          <div class="frame-total">/ {max_frame:04d} total</div>
        </div>
      </div>
      <input type="range" id="slider" min="0" max="{max_frame}" value="0" step="1">
      <div class="controls">
        <button class="ctrl-btn" id="btnPrev" onclick="stepFrame(-1)">◀ PREV</button>
        <button class="ctrl-btn" id="btnPlay" onclick="togglePlay()">▶ PLAY</button>
        <button class="ctrl-btn" id="btnNext" onclick="stepFrame(1)">NEXT ▶</button>
        <span class="fps-label" id="fpsLabel">5 FPS</span>
      </div>
    </div>

    <!-- Detection list -->
    <div class="det-panel">
      <div class="det-header">Detections</div>
      <div class="det-list" id="detList">
        <div class="det-empty">SELECT A FRAME</div>
      </div>
    </div>

  </div><!-- /bottom -->

</div><!-- /shell -->

<script>
// ── Data ─────────────────────────────────────────────────────────────────────
const FRAMES = {json.dumps(frames)};
const FUSED  = {json.dumps(fused_data)};
const LIDAR  = {json.dumps(lidar_data)};

// ── Class color map ───────────────────────────────────────────────────────────
const CLASS_COLORS = {{
  vehicle:    '#00d4ff',
  pedestrian: '#00ff9d',
  cyclist:    '#ffb300',
  truck:      '#ff7c00',
  bus:        '#a78bfa',
  motorcycle: '#f472b6',
  default:    '#ff4444'
}};

function classColor(cls) {{
  return CLASS_COLORS[(cls || '').toLowerCase()] || CLASS_COLORS.default;
}}

// ── Canvas refs ───────────────────────────────────────────────────────────────
const camCanvas   = document.getElementById('cameraCanvas');
const camCtx      = camCanvas.getContext('2d');
const lidarCanvas = document.getElementById('lidarCanvas');
const lidarCtx    = lidarCanvas.getContext('2d');

// ── Draw camera ───────────────────────────────────────────────────────────────
function drawCamera(frameIdx) {{
  const b64 = FRAMES[frameIdx];
  if (!b64) {{
    camCtx.clearRect(0, 0, camCanvas.width, camCanvas.height);
    return;
  }}

  const img = new Image();
  img.src   = 'data:image/jpeg;base64,' + b64;
  img.onload = function () {{
    camCanvas.width  = img.width;
    camCanvas.height = img.height;
    document.getElementById('camMeta').textContent =
      img.width + ' × ' + img.height;

    camCtx.drawImage(img, 0, 0);

    // Draw detections
    const fd = FUSED.find(f => f.frame_index == frameIdx);
    if (!fd || !fd.objects) return;

    fd.objects.forEach(obj => {{
      const [x1, y1, x2, y2] = obj.bbox_2d;
      const w   = x2 - x1;
      const h   = y2 - y1;
      const col = classColor(obj.class);
      const lbl = ((obj.class || 'OBJ') + ' ' +
                   (obj.confidence !== undefined
                     ? (obj.confidence * 100).toFixed(0) + '%'
                     : '')).trim();

      // Glowing box
      camCtx.save();
      camCtx.shadowColor  = col;
      camCtx.shadowBlur   = 8;
      camCtx.strokeStyle  = col;
      camCtx.lineWidth    = 2;
      camCtx.strokeRect(x1, y1, w, h);

      // Corner ticks
      const tick = Math.min(w, h) * 0.18;
      camCtx.lineWidth = 3;
      [[x1,y1],[x2,y1],[x1,y2],[x2,y2]].forEach(([cx,cy], i) => {{
        const sx = (i === 1 || i === 3) ? -1 : 1;
        const sy = (i === 2 || i === 3) ? -1 : 1;
        camCtx.beginPath();
        camCtx.moveTo(cx + sx*tick, cy);
        camCtx.lineTo(cx, cy);
        camCtx.lineTo(cx, cy + sy*tick);
        camCtx.stroke();
      }});
      camCtx.restore();

      // Label background
      camCtx.font       = 'bold 11px "Barlow Condensed", sans-serif';
      const tw = camCtx.measureText(lbl).width;
      camCtx.fillStyle  = col;
      camCtx.globalAlpha = 0.85;
      camCtx.fillRect(x1, y1 - 18, tw + 8, 18);
      camCtx.globalAlpha = 1;

      // Label text
      camCtx.fillStyle = '#000';
      camCtx.fillText(lbl, x1 + 4, y1 - 4);
    }});
  }};
}}

// ── Draw LiDAR bird's-eye ─────────────────────────────────────────────────────
function drawLidar(frameIdx) {{
  const W = lidarCanvas.width;
  const H = lidarCanvas.height;
  lidarCtx.clearRect(0, 0, W, H);

  // Background gradient
  const bg = lidarCtx.createRadialGradient(W/2, H/2, 10, W/2, H/2, W/2);
  bg.addColorStop(0,   '#071120');
  bg.addColorStop(1,   '#030810');
  lidarCtx.fillStyle = bg;
  lidarCtx.fillRect(0, 0, W, H);

  // Grid rings
  lidarCtx.strokeStyle = 'rgba(0,212,255,0.08)';
  lidarCtx.lineWidth   = 1;
  [40,80,120,160].forEach(r => {{
    lidarCtx.beginPath();
    lidarCtx.arc(W/2, H/2, r, 0, Math.PI * 2);
    lidarCtx.stroke();
  }});

  // Crosshair
  lidarCtx.strokeStyle = 'rgba(0,212,255,0.12)';
  lidarCtx.beginPath(); lidarCtx.moveTo(W/2, 0); lidarCtx.lineTo(W/2, H); lidarCtx.stroke();
  lidarCtx.beginPath(); lidarCtx.moveTo(0, H/2); lidarCtx.lineTo(W, H/2); lidarCtx.stroke();

  // Ego vehicle marker
  lidarCtx.fillStyle = '#00d4ff';
  lidarCtx.shadowColor = '#00d4ff';
  lidarCtx.shadowBlur  = 12;
  lidarCtx.beginPath();
  lidarCtx.moveTo(W/2, H/2 - 10);
  lidarCtx.lineTo(W/2 + 6, H/2 + 6);
  lidarCtx.lineTo(W/2 - 6, H/2 + 6);
  lidarCtx.closePath();
  lidarCtx.fill();
  lidarCtx.shadowBlur = 0;

  const fd = LIDAR.find(f => f.frame_index == frameIdx);
  if (!fd || !fd.objects) {{
    document.getElementById('statLidar').textContent = '0';
    return;
  }}

  document.getElementById('statLidar').textContent = fd.objects.length;

  // Scale: 1 meter = 8 pixels; origin at canvas center
  const SCALE  = 8;
  const OX     = W / 2;
  const OY     = H / 2;

  fd.objects.forEach(obj => {{
    const c   = obj.bbox_3d && obj.bbox_3d.center ? obj.bbox_3d.center : [0,0,0];
    const dim = obj.bbox_3d && obj.bbox_3d.dimensions ? obj.bbox_3d.dimensions : [1,1,1];
    const yaw = (obj.bbox_3d && obj.bbox_3d.yaw) ? obj.bbox_3d.yaw : 0;
    const col = classColor(obj.class);

    // Position in canvas (X-forward / Y-right → canvas x right, y up)
    const px = OX + c[1] * SCALE;
    const py = OY - c[0] * SCALE;

    // Rotated rectangle
    const bw = (dim[1] || 1) * SCALE;
    const bh = (dim[0] || 1) * SCALE;

    lidarCtx.save();
    lidarCtx.translate(px, py);
    lidarCtx.rotate(yaw);

    lidarCtx.shadowColor = col;
    lidarCtx.shadowBlur  = 6;
    lidarCtx.strokeStyle = col;
    lidarCtx.lineWidth   = 1.5;
    lidarCtx.strokeRect(-bw/2, -bh/2, bw, bh);

    // Heading arrow
    lidarCtx.strokeStyle = col;
    lidarCtx.lineWidth   = 1;
    lidarCtx.beginPath();
    lidarCtx.moveTo(0, 0);
    lidarCtx.lineTo(0, -bh/2 - 4);
    lidarCtx.stroke();

    lidarCtx.restore();

    // Dot at center
    lidarCtx.fillStyle   = col;
    lidarCtx.shadowColor = col;
    lidarCtx.shadowBlur  = 10;
    lidarCtx.beginPath();
    lidarCtx.arc(px, py, 3, 0, Math.PI * 2);
    lidarCtx.fill();
    lidarCtx.shadowBlur = 0;

    // Label
    lidarCtx.fillStyle = col;
    lidarCtx.font      = '10px "Share Tech Mono", monospace';
    lidarCtx.fillText((obj.class || '?').toUpperCase(), px + 5, py - 4);
  }});
}}

// ── Detection list ────────────────────────────────────────────────────────────
function updateDetList(frameIdx) {{
  const el = document.getElementById('detList');
  const fd = FUSED.find(f => f.frame_index == frameIdx);

  if (!fd || !fd.objects || fd.objects.length === 0) {{
    el.innerHTML = '<div class="det-empty">NO DETECTIONS</div>';
    document.getElementById('statObjects').textContent = '0';
    return;
  }}

  document.getElementById('statObjects').textContent = fd.objects.length;

  el.innerHTML = fd.objects.map(obj => {{
    const col  = classColor(obj.class);
    const conf = obj.confidence !== undefined
      ? (obj.confidence * 100).toFixed(1) + '%' : '—';
    const bb   = obj.bbox_2d || [0,0,0,0];
    const pos  = 'x:' + Math.round(bb[0]) + ' y:' + Math.round(bb[1]);
    return `<div class="det-item">
      <div class="det-dot" style="background:${{col}};box-shadow:0 0 5px ${{col}}"></div>
      <div class="det-class" style="color:${{col}}">${{(obj.class||'OBJ').toUpperCase()}}</div>
      <div class="det-pos">${{pos}}</div>
      <div class="det-conf">${{conf}}</div>
    </div>`;
  }}).join('');
}}

// ── Frame render ──────────────────────────────────────────────────────────────
function renderFrame(frameIdx) {{
  document.getElementById('statFrame').textContent    = frameIdx;
  document.getElementById('frameDisplay').textContent =
    String(frameIdx).padStart(4, '0');
  drawCamera(frameIdx);
  drawLidar(frameIdx);
  updateDetList(frameIdx);
}}

// ── Scrubber ──────────────────────────────────────────────────────────────────
const slider = document.getElementById('slider');
slider.addEventListener('input', function () {{
  renderFrame(parseInt(this.value));
}});

// ── Playback ──────────────────────────────────────────────────────────────────
let playing   = false;
let playTimer = null;
const FPS     = 5;

function togglePlay() {{
  playing = !playing;
  const btn = document.getElementById('btnPlay');
  if (playing) {{
    btn.textContent = '⏸ PAUSE';
    btn.classList.add('active');
    playTimer = setInterval(() => {{
      let v = parseInt(slider.value) + 1;
      if (v > {max_frame}) {{ v = 0; }}
      slider.value = v;
      renderFrame(v);
    }}, 1000 / FPS);
  }} else {{
    btn.textContent = '▶ PLAY';
    btn.classList.remove('active');
    clearInterval(playTimer);
  }}
}}

function stepFrame(delta) {{
  let v = Math.max(0, Math.min({max_frame}, parseInt(slider.value) + delta));
  slider.value = v;
  renderFrame(v);
}}

// Keyboard shortcuts
document.addEventListener('keydown', e => {{
  if (e.key === 'ArrowRight') stepFrame(1);
  if (e.key === 'ArrowLeft')  stepFrame(-1);
  if (e.key === ' ')          {{ e.preventDefault(); togglePlay(); }}
}});

// ── Initial render ────────────────────────────────────────────────────────────
renderFrame(0);
</script>
</body>
</html>"""

with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
    f.write(html)

print(f"✅  Viewer saved → {OUTPUT_HTML}")
print(f"    Open it in any browser — no server needed.")
print(f"    Keyboard: ← → to step frames, SPACE to play/pause")