# CamXtract — v0.0.1

> Visual Intelligence Control Node — Local Network Camera Streaming Desktop App

[![Download](https://img.shields.io/badge/Download-v0.0.1-brightgreen?style=for-the-badge&logo=github)](https://github.com/prifulnath/CamXtract/releases/tag/v0.0.1)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue?style=for-the-badge&logo=windows)](https://github.com/prifulnath/CamXtract/releases/tag/v0.0.1)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)

> 📥 **[Download CamXtract_v0.0.1.exe](https://github.com/prifulnath/CamXtract/releases/tag/v0.0.1)** — No installation required. Just download and run.

---

## 🧠 Overview

**CamXtract** is a fast, low-latency, peer-to-peer video streaming application that turns any mobile device into a live webcam feed viewable on any networked device (laptop, tablet, or secondary monitor).

Video routes **directly** over your local WiFi via **WebRTC** — no cloud, no lag, no external processing. A lightweight **FastAPI + WebSocket** server handles only the initial peer signaling.

---

## ✨ Features

| Feature | Details |
|---|---|
| **P2P Video Streaming** | Browser-to-browser via WebRTC — bare metal, no relays |
| **1080p Full HD / 4K UHD** | Explicit `getUserMedia` constraints; auto-falls back through resolution list if unsupported |
| **Adaptive Resolution** | Resolution, FPS, and codec configurable per-device via GUI, viewer UI, or `camxtract_config.json` |
| **Ultra-Low Latency** | `playoutDelayHint=0`, trickle ICE, `latencyMode:"realtime"`, DSCP `"high"` priority |
| **PC Remote Camera Controls** | Zoom, torch, exposure, resolution, FPS, flip — controllable from viewer page or desktop GUI |
| **Save / Restore Camera Params** | All camera settings auto-saved to `camxtract_config.json`; restored on next sender load |
| **Adaptive Bitrate (ABR)** | Bitrate scales automatically (500 Kbps–20 Mbps) based on network conditions |
| **Codec Preference** | VP9 (default), H.264, VP8, or auto — selectable per session |
| **Power & CPU Optimised** | Standby 5 fps until viewer connects; tab-hidden pause; inactivity auto-disconnect |
| **Camera Switching** | Flip front/rear without dropping the WebRTC stream |
| **iOS Compatibility** | Local SSL + autoplay policy handling for Safari |
| **Connection Queue** | Prevents stream hijacking; promotes next sender automatically |
| **Desktop GUI (CamXtract)** | `customtkinter` app — dark themed, custom title bar, sidebar nav |
| **Camera Controls Panel** | GUI panel for live remote control, codec/bitrate settings, save/load/reset profiles |
| **Camera Monitor Panel** | Embedded live feed via Edge WebView2 (`tkwebview2`) — no browser needed |
| **Lazy Panel Loading** | Panels load on first click — instant startup, splash screen on launch |
| **Server Settings** | Max Viewers, CPU Limiter sliders, Hardware Acceleration toggle, port allocation |
| **Secure Vault** | Stores SSL cert fingerprint & private key snippet with reveal/copy controls |
| **Security Log** | Alert cards with IP threat tracking, SSL certificate info |
| **Support Panel** | Troubleshooting tools, debug protocol, support channels, copyright footer |
| **OBS Integration** | Browser Source URL for OBS / streaming software |

---

## 📁 Project Structure

```text
CamXtract/
├── app/
│   ├── router.py             # FastAPI router aggregator
│   ├── api/
│   │   └── camera_config.py  # GET/PUT/reset /api/camera-config endpoint
│   ├── sender/               # Sender (Broadcaster) module
│   │   ├── sender.html / .js / .py
│   ├── viewer/               # Viewer (Watcher) module
│   │   ├── viewer.html / .js / .py
│   └── ws/                   # WebSocket signaling
│       ├── websocket.py
│       └── manager.py        # Routing: signaling + camera_control + heartbeat
│
├── ui/                       # Desktop GUI panels (customtkinter)
│   ├── ui_menu.py            # Sidebar navigation (lazy + version badge)
│   ├── ui_console.py         # Server orchestrator panel
│   ├── ui_server_settings.py # System parameters + footer stats bar
│   ├── ui_camera_controls.py # Camera remote control + save/load profile
│   ├── ui_network_info.py    # Network diagnostics
│   ├── ui_security_log.py    # Threat alert cards + SSL certificate info
│   ├── ui_vault.py           # Credential vault (reveal/copy/export)
│   ├── ui_support.py         # Diagnostics, debug protocol, support channels
│   └── ui_camera_monitor.py  # Live stream viewer (Edge WebView2)
│
├── gui.py                    # App entrypoint — splash screen + lazy loading
├── main.py                   # FastAPI app + lifespan (heartbeat, inactivity watcher)
├── run.py                    # CLI server runner
├── camxtract_config.json           # Runtime config (server, camera, streaming params)
├── version_info.txt          # Windows EXE version metadata (PyInstaller)
├── CamXtract.spec              # PyInstaller build spec
├── requirements.txt
└── README.md
```

---

## 🏗️ Architecture

```
[Mobile Browser / Sender]
    │  getUserMedia (adaptive res: 480p → 1080p → 4K)
    │  camera_control messages ← PC / GUI
    ▼
[WebRTC Peer Connection]  ←→  [FastAPI WS Signaling Server]
    │                          (heartbeat, inactivity watcher, camera_control relay)
    ▼
[Viewer Browser / CamXtract Desktop (WebView2)]
    │  PC Remote Control Bar (zoom, torch, exposure, resolution, FPS, flip)
    └─ CamXtract GUI: Camera Controls Panel (save / load / reset profile)
```

### Config Flow

```
camxtract_config.json  ←──→  GET/PUT /api/camera-config  ←──→  sender.js (auto-restore)
                                  ↕
                         GUI Camera Controls Panel
                         (Save Profile / Load Profile / Reset Defaults)
```

---

## 🚀 Setup & Installation

### 1. Create Virtual Environment

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

> **Note:** `pywebview` is pinned to `4.4.1` and `tkwebview2` to `3.5.0` for compatibility with the embedded camera monitor.

---

## 🌐 Running the Server (Development)

```powershell
python run.py
```

Or directly via uvicorn:

```powershell
uvicorn main:app --host 0.0.0.0 --port 8000 --ssl-keyfile key.pem --ssl-certfile cert.pem
```

### Endpoints

| Role | URL |
|---|---|
| **Sender (Mobile)** | `https://<YOUR_LOCAL_IP>:8000/sender.html` |
| **Viewer (Desktop)** | `https://<YOUR_LOCAL_IP>:8000/viewer.html` |
| **OBS Browser Source** | `https://<YOUR_LOCAL_IP>:8000/obs.html` |
| **Camera Config (GET)** | `https://<YOUR_LOCAL_IP>:8000/api/camera-config` |
| **Camera Config (PUT)** | `https://<YOUR_LOCAL_IP>:8000/api/camera-config` |
| **Camera Config Reset** | `https://<YOUR_LOCAL_IP>:8000/api/camera-config/reset` (POST) |

> First visit will prompt a self-signed cert warning — click **Advanced → Proceed**.

---

## 📦 Building the Standalone `.exe`

### Using the Spec File (Recommended)

```powershell
.venv\Scripts\pyinstaller CamXtract.spec
```

Output: `dist\CamXtract.exe`

> ⚠️ Close `CamXtract.exe` before rebuilding — Windows locks the file while it's open.

### Manual Build (with version info)

```powershell
.venv\Scripts\pyinstaller --version-file version_info.txt `
  --name "CamXtract" --icon "app\camxtract_logo.ico" --onefile --windowed `
  --add-data "app;app" --add-data "ui;ui" `
  --hidden-import "uvicorn.logging" --hidden-import "uvicorn.loops" `
  --hidden-import "uvicorn.loops.auto" --hidden-import "uvicorn.protocols" `
  --hidden-import "uvicorn.protocols.http" --hidden-import "uvicorn.protocols.http.auto" `
  --hidden-import "uvicorn.protocols.websockets" `
  --hidden-import "uvicorn.protocols.websockets.auto" `
  --hidden-import "uvicorn.lifespan" --hidden-import "uvicorn.lifespan.on" `
  --hidden-import "cryptography" --hidden-import "fastapi" `
  --hidden-import "starlette" --hidden-import "customtkinter" --hidden-import "PIL" `
  --hidden-import "webview" --hidden-import "webview.platforms" `
  --hidden-import "webview.platforms.winforms" `
  --hidden-import "webview.platforms.edgechromium" `
  --hidden-import "bottle" --hidden-import "clr_loader" --hidden-import "proxy_tools" `
  --hidden-import "tkwebview2" --hidden-import "tkwebview2.tkwebview2" `
  --hidden-import "tkwebview2.bind" `
  gui.py
```

### EXE Version Info (`version_info.txt`)

| Field | Value |
|---|---|
| Product Name | CamXtract |
| File Version | 0.0.1.0 |
| Company | MalluCodeX |
| Copyright | © 2026 MalluCodeX |

---

## 🖥️ Using `CamXtract.exe`

1. Place the `.exe` anywhere with **write access** (not `Program Files`)
2. Double-click to run — a splash screen appears while the app loads
3. On first run: SSL certs are auto-generated for your local IP
4. Click **START SERVER** in the Console panel
5. Open the Sender URL on mobile, Viewer URL on desktop

### Accepting the Self-Signed Certificate

| Browser | Steps |
|---|---|
| **Chrome** | `Advanced` → `Proceed to <IP> (unsafe)` |
| **Safari (iOS)** | `Show Details` → `Visit this website` |
| **Firefox** | `Advanced...` → `Accept the Risk and Continue` |

> If your IP changes, delete `key.pem` and `cert.pem` and relaunch to auto-regenerate.

---

## 🔑 Core Technologies

| Technology | Role |
|---|---|
| **WebRTC** | Peer-to-peer video streaming (VP9 / H.264 preferred) |
| **FastAPI + WebSocket** | Signaling server, camera_control relay, REST config API |
| **customtkinter** | Desktop GUI framework |
| **tkwebview2 / Edge WebView2** | Embedded camera feed viewer |
| **cryptography** | Local SSL certificate generation |
| **requests** | GUI → backend REST calls (save/load camera profile) |
| **PyInstaller** | Single-file Windows executable |

---

## 🔮 Future Enhancements

- Multi-viewer broadcasting (SFU / mediasoup)
- Audio streaming
- Stream recording (server-side capture)
- QR code for quick mobile connection
- Token-based stream authentication
- Virtual camera device output
- TURN server support for cross-network streaming
- Per-viewer resolution downscaling (simulcast)

---

## 📌 Notes for Developers

- `gui.py` uses lazy panel loading — panels instantiate on first click, not at startup
- `main.py` uses FastAPI `lifespan` to start `manager.heartbeat()` and `manager.inactivity_watcher()` as background tasks
- `main.py` is the FastAPI app factory; `ui_console.py` creates a fresh FastAPI instance inline to avoid `from main import app` failing in frozen executables
- `pywebview` must stay at `4.4.1` — newer versions break `tkwebview2 3.5.0` compatibility
- The custom title bar uses `overrideredirect(True)` — minimize uses Win32 `ShowWindow(hwnd, SW_MINIMIZE)` directly
- `ui_camera_controls.py` connects to the server over `wss://` using `websocket-client` as a `register_gui` client — it must be installed separately if needed: `pip install websocket-client`
- Camera config is persisted in `camxtract_config.json` under the `"CAMERA"` key; the REST endpoint at `/api/camera-config` is the canonical read/write interface
- When building the `.exe`, add `--hidden-import "requests"` to the PyInstaller command

---

*© 2026 MalluCodeX. All rights reserved.*
