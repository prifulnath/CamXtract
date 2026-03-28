# CamXtract — Feature Implementation Plan

**Project:** CamXtract  
**Stack:** Python · FastAPI · WebRTC · WebSocket · CustomTkinter GUI  
**Date:** 2026-03-24  
**Document covers:** Six major capability upgrades

---

## Table of Contents

1. [Feature 1 — 1080p Full HD & Adaptive Resolution](#feature-1)
2. [Feature 2 — 4K UHD Support](#feature-2)
3. [Feature 3 — Ultra-Low Latency Transfer](#feature-3)
4. [Feature 4 — Camera Controls & PC Remote Controls](#feature-4)
5. [Feature 5 — Save / Restore Camera Parameters](#feature-5)
6. [Feature 6 — Optimized Power & CPU Usage](#feature-6)
7. [Config Schema Reference](#config-schema)
8. [Dependency Updates](#dependency-updates)
9. [Verification Plan](#verification-plan)

---

<a name="feature-1"></a>
## Feature 1 — 1080p Full HD & Adaptive Resolution

### Goal
Capture and stream the highest resolution the attached camera supports, defaulting to **1080p Full HD (1920×1080)**. Users can override this from the GUI Settings panel and from [camxtract_config.json](file:///d:/MCX_Projects/CamXtract/camxtract_config.json). If the camera cannot honour the requested resolution, the system auto-negotiates down gracefully (adaptive fallback).

### Background
Currently [sender.js](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js) calls `getUserMedia` with no explicit resolution constraints, so browsers pick an arbitrary default (usually 480p or 720p). Explicitly requesting 1920×1080 (or 4K, see Feature 2) will force the browser to use the full sensor resolution if supported.

---

### 1.1 — [camxtract_config.json](file:///d:/MCX_Projects/CamXtract/camxtract_config.json) Changes

Add a `CAMERA` block for all resolution settings:

```jsonc
{
  "SERVER NAME": "CamXtract-01",
  "PORT ALLOCATION": "8000",
  "PROTOCOL": "Secure WebSocket (WSS)",
  "Auto-start Engine": 1,
  "Hardware Acceleration": 1,
  "Adaptive Bitrate": 1,
  "PRIMARY INPUT DEVICE": "",
  "CAMERA": {
    "resolution": "1920x1080",
    "preferred_fps": 30,
    "fallback_resolutions": ["1280x720", "854x480"],
    "use_ideal": true
  },
  "INACTIVITY TIMEOUT": "5 Minutes",
  "Auto-Reconnect": 1
}
```

| Key | Values | Description |
|---|---|---|
| `resolution` | `"1920x1080"`, `"2560x1440"`, `"3840x2160"` | Target capture resolution |
| `preferred_fps` | `24`, `30`, `60` | Target frame rate |
| `fallback_resolutions` | Array of strings | Tried in order if primary resolution fails |
| `use_ideal` | `true` / `false` | Use `ideal` vs `exact` in MediaTrackConstraints |

---

### 1.2 — Backend: New `/api/camera-config` Endpoint

**File:** `app/api/camera_config.py` _(NEW)_

```python
from fastapi import APIRouter
from pydantic import BaseModel
import json, pathlib

CONFIG_PATH = pathlib.Path("camxtract_config.json")
router = APIRouter(prefix="/api")

class CameraConfig(BaseModel):
    resolution: str = "1920x1080"
    preferred_fps: int = 30
    fallback_resolutions: list[str] = ["1280x720", "854x480"]
    use_ideal: bool = True

@router.get("/camera-config", response_model=CameraConfig)
def get_camera_config():
    cfg = json.loads(CONFIG_PATH.read_text())
    return cfg.get("CAMERA", CameraConfig().model_dump())

@router.put("/camera-config")
def set_camera_config(body: CameraConfig):
    cfg = json.loads(CONFIG_PATH.read_text())
    cfg["CAMERA"] = body.model_dump()
    CONFIG_PATH.write_text(json.dumps(cfg, indent=4))
    return {"status": "saved"}
```

Register it in [app/router.py](file:///d:/MCX_Projects/CamXtract/app/router.py):

```python
from app.api.camera_config import router as camera_config_router
router.include_router(camera_config_router)
```

---

### 1.3 — Frontend: [sender.js](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js) Adaptive Resolution

Replace the current `getUserMedia` call in [initCamera()](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js#10-27) and in the flip handler with an adaptive version:

```javascript
// Fetched once on load from /api/camera-config
let camConfig = { resolution: "1920x1080", preferred_fps: 30,
                  fallback_resolutions: ["1280x720", "854x480"], use_ideal: true };

async function loadCamConfig() {
    const res = await fetch("/api/camera-config");
    if (res.ok) camConfig = await res.json();
}

function buildConstraints(resStr, fps, useIdeal) {
    const [w, h] = resStr.split("x").map(Number);
    const mode = useIdeal ? "ideal" : "exact";
    return {
        video: {
            width: { [mode]: w },
            height: { [mode]: h },
            frameRate: { ideal: fps },
            facingMode: currentFacingMode
        },
        audio: false
    };
}

async function initCamera() {
    await loadCamConfig();
    const attempts = [camConfig.resolution, ...camConfig.fallback_resolutions];
    for (const res of attempts) {
        try {
            stream = await navigator.mediaDevices.getUserMedia(
                buildConstraints(res, camConfig.preferred_fps, camConfig.use_ideal)
            );
            console.log(`Camera opened at: ${res}`);
            break;
        } catch (e) {
            console.warn(`Resolution ${res} failed, trying next...`);
        }
    }
    if (!stream) { alert("No compatible camera resolution found."); return; }
    video.srcObject = stream;
    video.setAttribute("playsinline", "true");
    video.muted = true;
}
```

---

### 1.4 — GUI Settings Panel

**File:** [gui.py](file:///d:/MCX_Projects/CamXtract/gui.py) — add a "Resolution" dropdown to the Camera Settings tab:

```python
# Inside the Camera Settings frame
resolution_label = ctk.CTkLabel(cam_frame, text="Resolution")
resolution_var = ctk.StringVar(value=config["CAMERA"]["resolution"])
resolution_menu = ctk.CTkOptionMenu(
    cam_frame,
    values=["1920x1080", "2560x1440", "3840x2160", "1280x720", "854x480"],
    variable=resolution_var,
    command=lambda v: save_camera_setting("resolution", v)
)
fps_label = ctk.CTkLabel(cam_frame, text="Frame Rate (FPS)")
fps_var = ctk.StringVar(value=str(config["CAMERA"]["preferred_fps"]))
fps_menu = ctk.CTkOptionMenu(
    cam_frame,
    values=["24", "30", "60"],
    variable=fps_var,
    command=lambda v: save_camera_setting("preferred_fps", int(v))
)
```

`save_camera_setting()` makes a PUT call to `/api/camera-config` and writes the new value to [camxtract_config.json](file:///d:/MCX_Projects/CamXtract/camxtract_config.json), then triggers a `ws.send({ type: "reload_config" })` message so the live sender picks up the change without a full page reload.

---

<a name="feature-2"></a>
## Feature 2 — 4K UHD Support

### Goal
Allow the camera to capture and stream at **3840×2160 (4K UHD)** when the hardware supports it, with automatic bitrate and codec tuning to keep the stream stable.

### Background
4K over WebRTC requires:
1. Explicit `getUserMedia` constraints (handled by Feature 1's resolution system).
2. Higher bitrate cap on the RTCPeerConnection sender.
3. Preferring VP9 or H.264 HW-accelerated codecs over the default VP8.

---

### 2.1 — Bitrate Encoding Parameters in [sender.js](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js)

After the RTCPeerConnection offer is created, apply sender encoding parameters:

```javascript
async function applyEncodingParams(pc, stream) {
    const videoSender = pc.getSenders().find(s => s.track?.kind === "video");
    if (!videoSender) return;

    const params = videoSender.getParameters();
    if (!params.encodings || params.encodings.length === 0) {
        params.encodings = [{}];
    }

    const [w] = camConfig.resolution.split("x").map(Number);
    const is4K  = w >= 3840;
    const isHD  = w >= 1920;

    params.encodings[0].maxBitrate = is4K ? 20_000_000   // 20 Mbps for 4K
                                   : isHD ?  8_000_000   //  8 Mbps for 1080p
                                           :  3_000_000; //  3 Mbps for lower

    params.encodings[0].maxFramerate = camConfig.preferred_fps;

    await videoSender.setParameters(params);
}
```

Call `applyEncodingParams(pc, stream)` after `pc.setLocalDescription(offer)`.

---

### 2.2 — Prefer VP9 / H.264 Codec in [sender.js](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js)

```javascript
function preferCodec(sdp, codec) {
    const lines = sdp.split("\r\n");
    const mLineIndex = lines.findIndex(l => l.startsWith("m=video"));
    if (mLineIndex < 0) return sdp;

    const codecPayloads = lines
        .filter(l => new RegExp(`a=rtpmap:(\\d+) ${codec}`, "i").test(l))
        .map(l => l.match(/a=rtpmap:(\d+)/)[1]);

    if (codecPayloads.length === 0) return sdp; // Codec not supported, skip

    const mLine = lines[mLineIndex].split(" ");
    const otherPayloads = mLine.slice(3).filter(p => !codecPayloads.includes(p));
    lines[mLineIndex] = [...mLine.slice(0, 3), ...codecPayloads, ...otherPayloads].join(" ");
    return lines.join("\r\n");
}

// In startPeerConnection(), after createOffer():
offer.sdp = preferCodec(offer.sdp, "VP9");
// Fallback: preferCodec(offer.sdp, "H264");
await pc.setLocalDescription(offer);
```

---

### 2.3 — Config Flag for 4K Mode

```jsonc
"CAMERA": {
  "resolution": "3840x2160",
  "preferred_fps": 30,
  "codec_preference": "VP9",  // "VP9" | "H264" | "VP8" | "auto"
  ...
}
```

The `/api/camera-config` Pydantic model gets a `codec_preference: str = "VP9"` field. The GUI shows a "Codec" dropdown in camera settings.

---

<a name="feature-3"></a>
## Feature 3 — Ultra-Low Latency Transfer

### Goal
Minimise end-to-end glass-to-glass latency to **< 150 ms** on a local LAN.

### Root causes of latency in current implementation
| Source | Impact |
|---|---|
| Default ICE gathering waits for all candidates (trickle-ICE disabled) | +100-500 ms |
| No explicit RTP jitter buffer policy | +50-200 ms |
| No DSCP / traffic priority markings | Variable |
| No `latencyMode` on `getUserMedia` | Camera buffer adds 1-2 frames |

---

### 3.1 — Enable Trickle ICE in [sender.js](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js) and [viewer.js](file:///d:/MCX_Projects/CamXtract/app/viewer/viewer.js)

Currently the code waits for [onicecandidate](file:///d:/MCX_Projects/CamXtract/app/viewer/viewer.js#35-40) events but the offer is sent immediately — this is correct trickle-ICE behaviour. However, ensure **no `iceTransportPolicy: "relay"`** is set and that ICE candidates are sent as they arrive (they are), not batched.

Add a timeout to force-send the offer even before ICE gathering is complete if needed:

```javascript
// sender.js — startPeerConnection()
pc.onicegatheringstatechange = () => {
    if (pc.iceGatheringState === "complete") {
        console.log("ICE gathering complete");
    }
};
// Trickle ICE: send offer immediately after setLocalDescription
ws.send(JSON.stringify({ type: "offer", data: pc.localDescription }));
// Do NOT wait for gathering to finish before sending the offer!
```

---

### 3.2 — Jitter Buffer Target

Set the playout delay hint on the received video track (viewer side):

```javascript
// viewer.js — inside pc.ontrack
pc.ontrack = (event) => {
    video.srcObject = event.streams[0];
    // Ultra-low latency: reduce jitter buffer
    event.receiver.playoutDelayHint = 0;   // seconds; 0 = minimum buffering
    video.onloadedmetadata = () => video.play().catch(console.error);
};
```

---

### 3.3 — Camera Capture Latency Hint (`getUserMedia`)

```javascript
// sender.js — buildConstraints()
video: {
    width: { ideal: w },
    height: { ideal: h },
    frameRate: { ideal: fps },
    facingMode: currentFacingMode,
    latencyMode: "realtime"    // Chrome 120+ hint; reduces camera buffer latency
}
```

---

### 3.4 — DSCP / Traffic Priority

```javascript
// sender.js — after adding tracks to pc
stream.getTracks().forEach(track => {
    pc.addTrack(track, stream);
});
// Set RTP priority to "high" for video sender
pc.getSenders().forEach(sender => {
    const params = sender.getParameters();
    if (params.encodings) {
        params.encodings.forEach(enc => enc.priority = "high");
        sender.setParameters(params);
    }
});
```

---

### 3.5 — FastAPI / Uvicorn WebSocket Tuning

In [run.py](file:///d:/MCX_Projects/CamXtract/run.py), tune the Uvicorn startup:

```python
uvicorn.run(
    app,
    host="0.0.0.0",
    port=port,
    ssl_keyfile="key.pem",
    ssl_certfile="cert.pem",
    # Low-latency server tuning
    loop="uvloop",           # install uvloop for faster async on Linux/macOS
    http="httptools",
    ws="websockets",
    ws_ping_interval=5,      # seconds between WebSocket pings
    ws_ping_timeout=10,
    timeout_keep_alive=30,
)
```

> **Note:** `uvloop` is Linux/macOS only. On Windows it is silently ignored — use the default `asyncio` loop.

---

### 3.6 — WebSocket Manager Heartbeat

In [app/ws/manager.py](file:///d:/MCX_Projects/CamXtract/app/ws/manager.py), add a ping/keep-alive loop so connections don't go stale:

```python
import asyncio

async def heartbeat(self):
    """Send periodic pings to all clients to detect dead connections early."""
    while True:
        await asyncio.sleep(5)
        for ws in [self.active_sender, *self.viewers]:
            if ws:
                try:
                    await ws.send_text('{"type":"ping"}')
                except Exception:
                    await self.disconnect(ws)
```

Start this coroutine from the FastAPI `lifespan` or `startup` event.

---

<a name="feature-4"></a>
## Feature 4 — Camera Controls & PC Remote Controls

### Goal
Allow the **PC viewer** to send camera control commands to the **mobile sender** in real time:
- Zoom in / out
- Torch / flash toggle
- Exposure adjustment
- Focus (tap-to-focus equivalent)
- Resolution / FPS change at runtime
- **Flip camera** (already exists — integrate into unified control bus)

Also expose these same controls in the **CamXtract desktop GUI** so the operator can control the camera from their PC without touching the phone.

---

### 4.1 — Control Message Protocol (WebSocket)

Define a new `camera_control` message type. Messages flow: **PC → Server → Sender**.

```jsonc
// PC/Viewer sends:
{ "type": "camera_control", "action": "zoom", "value": 1.5 }
{ "type": "camera_control", "action": "torch", "value": true }
{ "type": "camera_control", "action": "exposure", "value": -1.0 }
{ "type": "camera_control", "action": "resolution", "value": "1920x1080" }
{ "type": "camera_control", "action": "fps", "value": 60 }
{ "type": "camera_control", "action": "flip", "value": null }
```

---

### 4.2 — [app/ws/manager.py](file:///d:/MCX_Projects/CamXtract/app/ws/manager.py) — Route Control Messages

```python
if data.get("type") == "camera_control":
    # Only viewers and the GUI are allowed to send controls
    if websocket in self.viewers or websocket in self.gui_clients:
        if self.active_sender:
            await self.active_sender.send_text(text_data)
    return
```

Add `self.gui_clients: list[WebSocket] = []` and a corresponding `register_gui` message type for the GUI's internal WebSocket connection.

---

### 4.3 — [sender.js](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js) — Handle Control Messages

```javascript
ws.onmessage = async (msg) => {
    const message = JSON.parse(msg.data);
    // ... existing handlers ...

    if (message.type === "camera_control") {
        await handleCameraControl(message.action, message.value);
    }
};

async function handleCameraControl(action, value) {
    switch (action) {
        case "zoom":
            applyZoom(value); break;
        case "torch":
            await applyTorch(value); break;
        case "exposure":
            await applyExposure(value); break;
        case "resolution":
            await switchResolution(value); break;
        case "fps":
            await switchFps(value); break;
        case "flip":
            document.getElementById("flip-btn").click(); break;
    }
}

// Zoom — digital zoom via MediaStreamTrack applyConstraints
function applyZoom(level) {
    const track = stream?.getVideoTracks()[0];
    if (!track) return;
    const caps = track.getCapabilities();
    if (caps.zoom) {
        const clampedZoom = Math.min(Math.max(level, caps.zoom.min), caps.zoom.max);
        track.applyConstraints({ advanced: [{ zoom: clampedZoom }] });
    }
}

// Torch — requires HTTPS and hardware support
async function applyTorch(on) {
    const track = stream?.getVideoTracks()[0];
    if (!track) return;
    const caps = track.getCapabilities();
    if (caps.torch) {
        await track.applyConstraints({ advanced: [{ torch: on }] });
    }
}

// Exposure
async function applyExposure(compensation) {
    const track = stream?.getVideoTracks()[0];
    if (!track) return;
    const caps = track.getCapabilities();
    if (caps.exposureCompensation) {
        const clamped = Math.min(Math.max(compensation,
            caps.exposureCompensation.min), caps.exposureCompensation.max);
        await track.applyConstraints({ advanced: [{ exposureCompensation: clamped }] });
    }
}

// Resolution change at runtime
async function switchResolution(resStr) {
    const [w, h] = resStr.split("x").map(Number);
    const track = stream?.getVideoTracks()[0];
    if (!track) return;
    await track.applyConstraints({ width: { ideal: w }, height: { ideal: h } });
    // Update WebRTC sender track params
    if (pc) {
        const sender = pc.getSenders().find(s => s.track?.kind === "video");
        if (sender) await sender.replaceTrack(stream.getVideoTracks()[0]);
    }
}
```

---

### 4.4 — [viewer.html](file:///d:/MCX_Projects/CamXtract/app/viewer/viewer.html) / [viewer.js](file:///d:/MCX_Projects/CamXtract/app/viewer/viewer.js) — PC Remote Control UI

Add a floating control panel to [viewer.html](file:///d:/MCX_Projects/CamXtract/app/viewer/viewer.html):

```html
<div id="remote-controls">
  <button id="btn-flip">🔄 Flip</button>
  <button id="btn-torch">🔦 Torch</button>
  <input type="range" id="zoom-slider" min="1" max="10" step="0.1" value="1">
  <input type="range" id="exposure-slider" min="-3" max="3" step="0.1" value="0">
  <select id="res-select">
    <option value="1920x1080">1080p</option>
    <option value="2560x1440">1440p</option>
    <option value="3840x2160">4K</option>
    <option value="1280x720">720p</option>
  </select>
</div>
```

Wire up in [viewer.js](file:///d:/MCX_Projects/CamXtract/app/viewer/viewer.js):

```javascript
function sendControl(action, value) {
    ws.send(JSON.stringify({ type: "camera_control", action, value }));
}
document.getElementById("btn-flip").onclick  = () => sendControl("flip", null);
document.getElementById("btn-torch").onclick = () => {
    torchOn = !torchOn;
    sendControl("torch", torchOn);
};
document.getElementById("zoom-slider").oninput = (e) => sendControl("zoom", parseFloat(e.target.value));
document.getElementById("exposure-slider").oninput = (e) => sendControl("exposure", parseFloat(e.target.value));
document.getElementById("res-select").onchange = (e) => sendControl("resolution", e.target.value);
```

---

### 4.5 — GUI (Desktop) Remote Control Panel

**File:** [gui.py](file:///d:/MCX_Projects/CamXtract/gui.py) — in the Camera Controls tab, add control sliders and buttons that internally connect a WebSocket to `/ws` registered as a GUI client and emit `camera_control` messages:

```python
# Zoom slider
zoom_slider = ctk.CTkSlider(ctrl_frame, from_=1.0, to=10.0, command=lambda v: send_ws_control("zoom", v))

# Torch toggle
torch_btn = ctk.CTkButton(ctrl_frame, text="🔦 Torch", command=lambda: send_ws_control("torch", not torch_state))

# Exposure
exposure_slider = ctk.CTkSlider(ctrl_frame, from_=-3.0, to=3.0, command=lambda v: send_ws_control("exposure", v))

# Resolution dropdown
res_menu = ctk.CTkOptionMenu(ctrl_frame, values=["1920x1080","2560x1440","3840x2160","1280x720"],
                              command=lambda v: send_ws_control("resolution", v))
```

`send_ws_control` sends a `camera_control` JSON message via a `websockets` client running in a background thread.

---

<a name="feature-5"></a>
## Feature 5 — Save / Restore Camera Parameters

### Goal
All camera settings (resolution, FPS, zoom, exposure, codec, torch state, flip state, etc.) are **persisted to [camxtract_config.json](file:///d:/MCX_Projects/CamXtract/camxtract_config.json)** via the `/api/camera-config` PUT endpoint. On next launch, the sender page automatically reads these saved values and restores the camera to its last known state.

---

### 5.1 — Extended Config Schema

```jsonc
"CAMERA": {
  "resolution": "1920x1080",
  "preferred_fps": 30,
  "codec_preference": "VP9",
  "use_ideal": true,
  "fallback_resolutions": ["1280x720", "854x480"],
  "zoom": 1.0,
  "exposure_compensation": 0.0,
  "torch": false,
  "facing_mode": "environment",
  "max_bitrate_mbps": 8
}
```

---

### 5.2 — Auto-Save on Control Change

In [sender.js](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js), after every successful `applyConstraints` call, POST the current state back:

```javascript
async function saveCameraState() {
    const track = stream?.getVideoTracks()[0];
    const settings = track ? track.getSettings() : {};
    await fetch("/api/camera-config", {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            resolution: `${settings.width || 1920}x${settings.height || 1080}`,
            preferred_fps: settings.frameRate || 30,
            zoom: settings.zoom || 1.0,
            exposure_compensation: settings.exposureCompensation || 0.0,
            torch: settings.torch || false,
            facing_mode: currentFacingMode,
            codec_preference: camConfig.codec_preference || "VP9",
            use_ideal: camConfig.use_ideal ?? true,
            fallback_resolutions: camConfig.fallback_resolutions || ["1280x720", "854x480"],
            max_bitrate_mbps: camConfig.max_bitrate_mbps || 8
        })
    });
}
```

Call `saveCameraState()` after `applyZoom`, `applyTorch`, `applyExposure`, and `switchResolution`.

---

### 5.3 — Restore on Load

In [initCamera()](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js#10-27), after opening the stream, restore persisted controls:

```javascript
async function restorePersistedControls() {
    // Zoom
    if (camConfig.zoom && camConfig.zoom > 1.0) applyZoom(camConfig.zoom);
    // Torch
    if (camConfig.torch) await applyTorch(true);
    // Exposure
    if (camConfig.exposure_compensation !== 0) await applyExposure(camConfig.exposure_compensation);
    // Facing mode
    currentFacingMode = camConfig.facing_mode || "environment";
}
// Call after initCamera() completes successfully
await restorePersistedControls();
```

---

### 5.4 — GUI "Save Profile" & "Load Profile"

In [gui.py](file:///d:/MCX_Projects/CamXtract/gui.py), add two buttons in the Camera Settings panel:

```python
save_profile_btn = ctk.CTkButton(
    cam_frame, text="💾 Save Camera Profile",
    command=lambda: requests.put(f"https://localhost:{port}/api/camera-config",
                                  json=get_current_cam_settings(), verify=False)
)
load_profile_btn = ctk.CTkButton(
    cam_frame, text="📂 Load Camera Profile",
    command=lambda: populate_camera_settings(
        requests.get(f"https://localhost:{port}/api/camera-config", verify=False).json()
    )
)
```

Also provide a **"Reset to Defaults"** button that sends:
```python
{ "resolution": "1920x1080", "preferred_fps": 30, "zoom": 1.0, "exposure_compensation": 0.0, "torch": False }
```

---

<a name="feature-6"></a>
## Feature 6 — Optimized Power & CPU Usage

### Goal
Minimise CPU and battery drain on both the PC server and the mobile sender without sacrificing stream quality. Key strategies: adaptive bitrate, CPU-aware frame dropping, inactivity sleep, and hardware acceleration.

---

### 6.1 — Adaptive Bitrate (ABR) on WebRTC Sender

```javascript
// sender.js — start a bandwidth estimation loop
function startABRLoop(pc) {
    setInterval(async () => {
        if (!pc) return;
        const stats = await pc.getStats(null);
        stats.forEach(report => {
            if (report.type === "outbound-rtp" && report.kind === "video") {
                const bps = report.bytesSent / (report.timestamp / 1000);
                const sender = pc.getSenders().find(s => s.track?.kind === "video");
                if (!sender) return;
                const params = sender.getParameters();
                if (params.encodings?.length > 0) {
                    // Scale bitrate: cap at 20 Mbps, floor at 500 Kbps
                    const targetBps = Math.min(20_000_000,
                                       Math.max(500_000, bps * 1.2));
                    params.encodings[0].maxBitrate = targetBps;
                    sender.setParameters(params);
                }
            }
        });
    }, 3000); // Evaluate every 3 seconds
}
```

Call `startABRLoop(pc)` after [startPeerConnection()](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js#28-49).

---

### 6.2 — Viewer-Side Inactive Frame Drop

When the viewer tab is hidden (e.g., user switches apps), WebRTC already throttles. Reinforce with:

```javascript
// viewer.js
document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
        video.pause();
    } else {
        video.play().catch(() => {});
    }
});
```

---

### 6.3 — Inactivity Timeout (Server-Side)

**File:** [app/ws/manager.py](file:///d:/MCX_Projects/CamXtract/app/ws/manager.py) — track last activity and disconnect idle clients:

```python
import time

class ConnectionManager:
    def __init__(self):
        self.active_sender = None
        self.waiting_senders = []
        self.viewers = []
        self.last_activity: dict = {}  # ws -> timestamp
        self.TIMEOUT_SECONDS = 300     # 5 minutes, configurable

    async def touch(self, ws):
        self.last_activity[ws] = time.monotonic()

    async def inactivity_watcher(self):
        while True:
            await asyncio.sleep(30)
            now = time.monotonic()
            stale = [ws for ws, t in self.last_activity.items()
                     if now - t > self.TIMEOUT_SECONDS]
            for ws in stale:
                try:
                    await ws.send_text('{"type":"timeout","message":"Connection timed out due to inactivity."}')
                    await ws.close()
                except Exception:
                    pass
                await self.disconnect(ws)
```

Read `INACTIVITY TIMEOUT` from [camxtract_config.json](file:///d:/MCX_Projects/CamXtract/camxtract_config.json) and convert to seconds.

---

### 6.4 — Hardware Acceleration Flag

In [camxtract_config.json](file:///d:/MCX_Projects/CamXtract/camxtract_config.json), `"Hardware Acceleration": 1` is already present. Activate it:

- **Sender [sender.js](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js)**: Always prefer VP9/H.264 (both have HW encoder support in Chrome on Android) — done in Feature 2.
- **Viewer [viewer.js](file:///d:/MCX_Projects/CamXtract/app/viewer/viewer.js)**: No special flag needed — HW decoding is automatic when the codec matches the OS decoder.
- **Server [main.py](file:///d:/MCX_Projects/CamXtract/main.py)**: No video processing occurs on the server (pure relay), so CPU is minimal.

---

### 6.5 — FPS Cap When No Viewer Is Connected

In [sender.js](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js), when in `isSending` state but no viewer has connected yet, reduce camera FPS to a standby rate:

```javascript
const STANDBY_FPS = 5;  // Low FPS while waiting for viewer

ws.onmessage = async (msg) => {
    const message = JSON.parse(msg.data);
    if (message.type === "start_sending") {
        isSending = true;
        document.getElementById("status-overlay").style.display = "none";
        await initCamera();
        // Apply standby FPS until viewer connects
        const track = stream?.getVideoTracks()[0];
        track?.applyConstraints({ frameRate: { max: STANDBY_FPS } });
    }
    if (message.type === "viewer_ready") {
        // Restore full FPS now that viewer is watching
        const track = stream?.getVideoTracks()[0];
        track?.applyConstraints({ frameRate: { ideal: camConfig.preferred_fps } });
        startPeerConnection();
    }
};
```

---

### 6.6 — Uvicorn Worker Configuration

In [run.py](file:///d:/MCX_Projects/CamXtract/run.py), use `workers=1` (single process) since WebSocket state is in-process. Avoid multi-worker unless a Redis-backed pub/sub is added. This keeps RAM usage predictable.

---

<a name="config-schema"></a>
## Config Schema Reference — Full [camxtract_config.json](file:///d:/MCX_Projects/CamXtract/camxtract_config.json)

```jsonc
{
    "SERVER NAME": "CamXtract-01",
    "PORT ALLOCATION": "8000",
    "PROTOCOL": "Secure WebSocket (WSS)",
    "Auto-start Engine": 1,
    "Hardware Acceleration": 1,
    "Adaptive Bitrate": 1,
    "PRIMARY INPUT DEVICE": "",
    "CAMERA": {
        "resolution": "1920x1080",
        "preferred_fps": 30,
        "codec_preference": "VP9",
        "use_ideal": true,
        "fallback_resolutions": ["1280x720", "854x480"],
        "zoom": 1.0,
        "exposure_compensation": 0.0,
        "torch": false,
        "facing_mode": "environment",
        "max_bitrate_mbps": 8
    },
    "INACTIVITY TIMEOUT": "5 Minutes",
    "Auto-Reconnect": 1
}
```

---

<a name="dependency-updates"></a>
## Dependency Updates ([requirements.txt](file:///d:/MCX_Projects/CamXtract/requirements.txt))

| Package | Reason |
|---|---|
| `requests==2.32.4` | GUI → backend HTTP calls (save/load profile) |
| `uvloop==0.21.0` | Faster async event loop on Linux/macOS (optional on Windows) |

Add to [requirements.txt](file:///d:/MCX_Projects/CamXtract/requirements.txt):
```
requests==2.32.4
# uvloop==0.21.0  # Linux/macOS only, comment out for Windows builds
```

---

<a name="verification-plan"></a>
## Verification Plan

### Feature 1 — 1080p Resolution
- [ ] Open [sender.html](file:///d:/MCX_Projects/CamXtract/app/sender/sender.html) on mobile, check DevTools → Media → `getUserMedia` track settings show `width: 1920, height: 1080`.
- [ ] Change resolution to 720p from GUI settings, verify sender logs `"Camera opened at: 1280x720"`.
- [ ] Test with a camera that does NOT support 1080p → verify fallback to 720p without crash.

### Feature 2 — 4K UHD
- [ ] Set `resolution: "3840x2160"` in config; verify track settings on a 4K-capable device.
- [ ] Inspect SDP offer in console → confirm VP9 codec appears first in `m=video` line.
- [ ] Monitor `getStats()` → `bytesSent` rate approaches ~15-20 Mbps under 4K.

### Feature 3 — Ultra-Low Latency
- [ ] Clap in front of camera; observe glass-to-glass delay visually on viewer — target < 200 ms.
- [ ] Check `playoutDelayHint` is accepted (Chrome DevTools → Media → `jitterBufferDelay`).
- [ ] Verify trickle ICE: viewer receives video before ICE gathering completes.

### Feature 4 — Camera Controls
- [ ] From [viewer.html](file:///d:/MCX_Projects/CamXtract/app/viewer/viewer.html), move zoom slider → confirm camera zooms on mobile.
- [ ] Toggle torch button → flashlight activates on device.
- [ ] Change resolution from viewer → stream switches resolution without reconnect.
- [ ] GUI controls (zoom, flip, torch) → same effects as viewer controls.

### Feature 5 — Save / Restore
- [ ] Set zoom to 2.0, torch ON, resolution 4K, then close tab.
- [ ] Reopen [sender.html](file:///d:/MCX_Projects/CamXtract/app/sender/sender.html) → camera auto-restores to zoom 2.0, torch ON, 4K.
- [ ] "Reset to Defaults" button returns all values to baseline.

### Feature 6 — Power & CPU
- [ ] Monitor Task Manager on PC: server CPU < 5% with one sender + viewer streaming 1080p.
- [ ] After 5 minutes of no activity, verify sender receives `"timeout"` message and connection closes.
- [ ] FPS during standby (no viewer) drops to ~5 FPS, then restores to 30 when viewer connects.
- [ ] Adaptive bitrate: throttle network to 5 Mbps → encoder bitrate scales down within 1-2 cycles.

---

*End of document — CamXtract Feature Implementation Plan v1.0*
