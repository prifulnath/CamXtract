# CamXtract — Feature Implementation Walkthrough

All 6 features from the approved plan have been implemented. Here is a summary of what changed and how each feature works.

---

## Files Changed

| File | Status | Feature(s) |
|---|---|---|
| [camxtract_config.json](file:///d:/MCX_Projects/CamXtract/camxtract_config.json) | **Modified** | All — extended with full `CAMERA` block |
| [main.py](file:///d:/MCX_Projects/CamXtract/main.py) | **Modified** | F3, F6 — FastAPI lifespan starts heartbeat & inactivity watcher |
| [app/api/__init__.py](file:///d:/MCX_Projects/CamXtract/app/api/__init__.py) | **New** | F1, F2, F5 — Python package init |
| [app/api/camera_config.py](file:///d:/MCX_Projects/CamXtract/app/api/camera_config.py) | **New** | F1, F2, F5 — GET/PUT/reset REST API for camera config |
| [app/router.py](file:///d:/MCX_Projects/CamXtract/app/router.py) | **Modified** | F1 — registers new camera_config router |
| [app/ws/manager.py](file:///d:/MCX_Projects/CamXtract/app/ws/manager.py) | **Modified** | F3, F4, F6 — camera_control routing, gui_clients, heartbeat, inactivity watcher |
| [app/sender/sender.js](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js) | **Modified** | F1–F6 — full rewrite with all features |
| [app/viewer/viewer.js](file:///d:/MCX_Projects/CamXtract/app/viewer/viewer.js) | **Modified** | F3, F4, F6 — low-latency hints, control wiring, visibility pause |
| [app/viewer/viewer.html](file:///d:/MCX_Projects/CamXtract/app/viewer/viewer.html) | **Modified** | F4 — PC remote control bar UI |
| [ui/ui_camera_controls.py](file:///d:/MCX_Projects/CamXtract/ui/ui_camera_controls.py) | **New** | F4, F5 — GUI Camera Controls + Save/Load/Reset panel |
| [ui/ui_menu.py](file:///d:/MCX_Projects/CamXtract/ui/ui_menu.py) | **Modified** | F4 — added Camera Controls to sidebar nav |
| [gui.py](file:///d:/MCX_Projects/CamXtract/gui.py) | **Modified** | F4 — registered CameraControlsFrame in lazy-load map |
| [requirements.txt](file:///d:/MCX_Projects/CamXtract/requirements.txt) | **Modified** | F6 — added requests, urllib3, certifi |

---

## Per-Feature Summary

### ✅ F1 — 1080p Full HD & Adaptive Resolution
- [sender.js](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js) now calls `GET /api/camera-config` on load and builds `getUserMedia` constraints with explicit `width/height/frameRate`.
- Falls back through `fallback_resolutions` in order if the primary resolution is unsupported.
- [camxtract_config.json](file:///d:/MCX_Projects/CamXtract/camxtract_config.json) `CAMERA.resolution` defaults to `"1920x1080"`.
- GUI Camera Controls panel exposes a Resolution dropdown that sends `camera_control { action: "resolution" }` at runtime.

### ✅ F2 — 4K UHD Support
- Setting `resolution: "3840x2160"` in config (or from the viewer/GUI dropdown) requests 4K from the camera.
- [startPeerConnection()](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js#289-338) applies `maxBitrate = 20 Mbps` for 4K, `8 Mbps` for 1080p, `3 Mbps` for lower.
- SDP is rewritten by [preferCodec()](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js#221-237) to push VP9 (or configured codec) to the top of the `m=video` payload list.

### ✅ F3 — Ultra-Low Latency
- `getUserMedia` uses `latencyMode: "realtime"` to minimize camera buffer delay.
- Viewer sets `event.receiver.playoutDelayHint = 0` on received tracks to request minimum jitter buffering.
- WebRTC offer is sent immediately after `setLocalDescription` (true trickle ICE — no waiting for gathering to complete).
- RTP sender `priority` is set to `"high"` for DSCP marking.
- [manager.py](file:///d:/MCX_Projects/CamXtract/app/ws/manager.py) sends heartbeat pings every 5 s to detect stale connections early.

### ✅ F4 — Camera Controls & PC Remote Controls
- New `camera_control` WebSocket message type is routed by [manager.py](file:///d:/MCX_Projects/CamXtract/app/ws/manager.py) from viewers/GUI → active sender.
- [sender.js](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js) handles: `zoom`, [torch](file:///d:/MCX_Projects/CamXtract/ui/ui_camera_controls.py#357-364), `exposure`, [resolution](file:///d:/MCX_Projects/CamXtract/ui/ui_camera_controls.py#365-370), [fps](file:///d:/MCX_Projects/CamXtract/ui/ui_camera_controls.py#371-375), `flip`.
- [viewer.html](file:///d:/MCX_Projects/CamXtract/app/viewer/viewer.html) has a glassmorphism control bar at the bottom with: Flip, Torch, Zoom slider, Exposure slider, Resolution dropdown, FPS dropdown.
- New **Camera Controls** panel in the GUI sidebar connects via `wss://` as a `register_gui` client and sends the same `camera_control` messages.

### ✅ F5 — Save / Restore Camera Parameters
- Extended [camxtract_config.json](file:///d:/MCX_Projects/CamXtract/camxtract_config.json) `CAMERA` block stores: resolution, fps, codec, zoom, exposure, torch, facing_mode, max_bitrate_mbps.
- [sender.js](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js) calls [saveCameraState()](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js#41-67) (HTTP PUT) after every control change.
- On page load [restorePersistedControls()](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js#121-132) re-applies saved zoom, torch, and exposure to the live track.
- GUI panel: **Save Profile**, **Load Profile**, **Reset Defaults** buttons hit `PUT /api/camera-config`, `GET /api/camera-config`, and `POST /api/camera-config/reset` respectively.

### ✅ F6 — Power & CPU Optimization
- Standby FPS mode: camera runs at 5 fps when no viewer is connected; restores to configured FPS on `viewer_ready`.
- ABR loop ([startABRLoop](file:///d:/MCX_Projects/CamXtract/app/sender/sender.js#266-286)) polls `getStats()` every 3 s and adjusts `maxBitrate`.
- Viewer pauses video playback when the tab is hidden (`visibilitychange` event).
- [manager.py](file:///d:/MCX_Projects/CamXtract/app/ws/manager.py) inactivity watcher disconnects silent clients after the configured timeout (from [camxtract_config.json](file:///d:/MCX_Projects/CamXtract/camxtract_config.json)).
- Server `uvicorn` note: `uvloop` is available for Linux/macOS (commented out in requirements for Windows compatibility).

---

## Verification Results

```
Syntax check — all modified Python files:
  OK: main.py
  OK: run.py
  OK: app/ws/manager.py
  OK: app/api/camera_config.py
  OK: app/router.py
  OK: ui/ui_camera_controls.py
  All syntax OK

CameraConfig model import:
  CameraConfig OK: {'resolution': '1920x1080', 'preferred_fps': 30,
  'codec_preference': 'VP9', 'use_ideal': True,
  'fallback_resolutions': ['1280x720', '854x480'],
  'zoom': 1.0, 'exposure_compensation': 0.0,
  'torch': False, 'facing_mode': 'environment', 'max_bitrate_mbps': 8}
```

---

## Next Steps (Manual)

1. Install new deps: `pip install requests urllib3 certifi charset-normalizer`
2. Start the server: click **Start Server** in the Console panel (or run `python run.py`)
3. Open [sender.html](file:///d:/MCX_Projects/CamXtract/app/sender/sender.html) on your phone — check the browser DevTools track settings show `1920×1080`
4. Open [viewer.html](file:///d:/MCX_Projects/CamXtract/app/viewer/viewer.html) on the PC — use the control bar to test zoom/torch/resolution
5. In the GUI, navigate to **Camera Controls** → adjust settings and click **Save Profile**
