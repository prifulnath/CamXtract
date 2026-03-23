# MCX Cam — v0.0.1

> Visual Intelligence Control Node — Local Network Camera Streaming Desktop App

[![Download](https://img.shields.io/badge/Download-v0.0.1-brightgreen?style=for-the-badge&logo=github)](https://github.com/prifulnath/MCX_Cam/releases/tag/v0.0.1)
[![Platform](https://img.shields.io/badge/Platform-Windows%2010%2F11-blue?style=for-the-badge&logo=windows)](https://github.com/prifulnath/MCX_Cam/releases/tag/v0.0.1)

> 📥 **[Download MCX_Cam_v0.0.1.exe](https://github.com/prifulnath/MCX_Cam/releases/tag/v0.0.1)** — No installation required. Just download and run.

---

## 🧠 Overview

**MCX Cam** is a fast, low-latency, peer-to-peer video streaming application that turns any mobile device into a live webcam feed viewable on any networked device (laptop, tablet, or secondary monitor).

Video routes **directly** over your local WiFi via **WebRTC** — no cloud, no lag, no external processing. A lightweight **FastAPI + WebSocket** server handles only the initial peer signaling.

---

## ✨ Features

| Feature | Details |
|---|---|
| **P2P Video Streaming** | Browser-to-browser via WebRTC — bare metal, no relays |
| **Camera Switching** | Flip front/rear without dropping the stream |
| **iOS Compatibility** | Local SSL + autoplay policy handling for Safari |
| **Connection Queue** | Prevents stream hijacking; promotes next sender automatically |
| **Desktop GUI (MCX CAM)** | `customtkinter` app — dark themed, custom title bar, sidebar nav |
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
MCX_Cam/
├── app/
│   ├── router.py             # FastAPI router aggregator
│   ├── sender/               # Sender (Broadcaster) module
│   │   ├── sender.html / .js / .py
│   ├── viewer/               # Viewer (Watcher) module
│   │   ├── viewer.html / .js / .py
│   └── ws/                   # WebSocket signaling
│       ├── websocket.py
│       └── manager.py
│
├── ui/                       # Desktop GUI panels (customtkinter)
│   ├── ui_menu.py            # Sidebar navigation (lazy + version badge)
│   ├── ui_console.py         # Server orchestrator panel
│   ├── ui_server_settings.py # System parameters + footer stats bar
│   ├── ui_network_info.py    # Network diagnostics
│   ├── ui_security_log.py    # Threat alert cards + SSL certificate info
│   ├── ui_vault.py           # Credential vault (reveal/copy/export)
│   ├── ui_support.py         # Diagnostics, debug protocol, support channels
│   └── ui_camera_monitor.py  # Live stream viewer (Edge WebView2)
│
├── gui.py                    # App entrypoint — splash screen + lazy loading
├── main.py                   # FastAPI app creation
├── run.py                    # CLI server runner
├── version_info.txt          # Windows EXE version metadata (PyInstaller)
├── MCX_Cam.spec              # PyInstaller build spec
├── requirements.txt
└── README.md
```

---

## 🏗️ Architecture

```
[Mobile Browser (Sender)]
    │ getUserMedia (camera)
    ▼
[WebRTC Peer Connection] ←→ [FastAPI WebSocket Signaling Server]
    ▲
    │
[Viewer Browser / MCX Cam Desktop (WebView2)]
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

> First visit will prompt a self-signed cert warning — click **Advanced → Proceed**.

---

## 📦 Building the Standalone `.exe`

### Using the Spec File (Recommended)

```powershell
.venv\Scripts\pyinstaller MCX_Cam.spec
```

Output: `dist\MCX_Cam.exe`

> ⚠️ Close `MCX_Cam.exe` before rebuilding — Windows locks the file while it's open.

### Manual Build (with version info)

```powershell
.venv\Scripts\pyinstaller --version-file version_info.txt `
  --name "MCX_Cam" --icon "app\mcx_logo.ico" --onefile --windowed `
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
| Product Name | MCX Cam |
| File Version | 0.0.1.0 |
| Company | MalluCodeX |
| Copyright | © 2026 MalluCodeX |

---

## 🖥️ Using `MCX_Cam.exe`

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
| **WebRTC** | Peer-to-peer video streaming |
| **FastAPI + WebSocket** | Signaling server only |
| **customtkinter** | Desktop GUI framework |
| **tkwebview2 / Edge WebView2** | Embedded camera feed viewer |
| **cryptography** | Local SSL certificate generation |
| **PyInstaller** | Single-file Windows executable |

---

## 🔮 Future Enhancements

- Multi-viewer broadcasting (SFU)
- Audio streaming
- Stream recording
- QR code for quick mobile connection
- Token-based stream authentication
- Virtual camera device output

---

## 📌 Notes for Developers

- `gui.py` uses lazy panel loading — panels instantiate on first click, not at startup
- `main.py` is the FastAPI app factory; `ui_console.py` creates a fresh FastAPI instance inline to avoid `from main import app` failing in frozen executables
- `pywebview` must stay at `4.4.1` — newer versions break `tkwebview2 3.5.0` compatibility
- The custom title bar uses `overrideredirect(True)` — minimize uses Win32 `ShowWindow(hwnd, SW_MINIMIZE)` directly

---

*© 2026 MalluCodeX. All rights reserved.*
