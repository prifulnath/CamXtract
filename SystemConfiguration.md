# CamXtract – System Sections Specification

This document defines the structure and features for the following sections:

* Server Settings
* Network Info
* Security Log
* Vault
* Support

---

# ⚙️ Server Settings (Core Control Panel)

## 🔧 Basic Controls

* Server Name (editable, e.g., CamXtract-01)
* Port Configuration (default: 8000)
* Protocol Selection:

  * HTTP
  * HTTPS
  * WebRTC
* Auto-start on launch (toggle)

## 📷 Camera / Stream Settings

* Default Resolution:

  * 480p / 720p / 1080p
* Frame Rate:

  * 15 / 30 / 60 FPS
* Bitrate:

  * Auto / Manual input
* Camera Selection:

  * Front / Rear (for mobile sender)

## 🔁 Streaming Behavior

* Maximum concurrent viewers
* Stream timeout (auto disconnect idle clients)
* Reconnection attempts (retry logic)

## ⚡ Performance

* Hardware acceleration (toggle)
* CPU usage limiter
* Bandwidth limiter
* Adaptive bitrate (recommended enabled)

---

# 🌐 Network Info (Diagnostics & Connectivity)

## 📡 Basic Info

* Local IP Address
* Public IP Address (via external API)
* Hostname
* MAC Address (optional)

## 🔌 Ports & Protocols

* Active Ports (e.g., 8000, WebSocket)
* Protocol in use (HTTP / WebRTC / WS)

## 📶 Connection Health

* Latency (ms)
* Packet Loss (%)
* Jitter (ms)

## 🔍 Device Discovery

* Connected Devices List:

  * Device Name
  * IP Address
  * Role (Sender / Viewer)
* Network Type:

  * WiFi / Ethernet / Mobile Hotspot

## 🔥 Advanced

* NAT Type Detection:

  * Open / Moderate / Strict
* STUN/TURN Server Status (if WebRTC enabled)

---

# 🔐 Security Log (Audit & Monitoring)

## 📜 Logs

* Device connection history
* IP access logs
* Failed connection attempts
* Session start/stop logs

## 🚨 Alerts

* Suspicious IP detection
* Excessive connection attempts
* Unauthorized access attempts

## 🔑 SSL Information

* Certificate Status (Valid / Invalid)
* Expiry Date
* Issuer (Self-signed / CA)

## 🧾 Actions

* Block IP Address
* Allowlist trusted devices
* Export logs (JSON / CSV)

---

# 🔒 Vault (Secrets & Secure Storage)

## 🔑 Stored Items

* SSL Certificates
* API Keys (future integrations)
* TURN/STUN credentials
* Access tokens

## 🔐 Features

* Encryption (AES-256 recommended)
* Masked values (••••••)
* Copy to clipboard
* Expiry / rotation support

## 🧠 Advanced

* Role-based access control:

  * Admin
  * Viewer
  * Sender

---

# 🆘 Support (Help & Debugging)

## 📘 Documentation

* How to connect mobile sender
* How to access viewer
* Fix SSL warning issues
* Common troubleshooting steps

## 🧰 Troubleshooting Tools

* Test Camera
* Test Network
* Test Stream

## 🐞 Debug Tools

* Export system logs
* Generate system info report

## 💬 Contact

* Email support
* Issue reporting (Git-based)
* FAQ section

---

# 💡 Bonus Features

## 🔥 Recommended Additions

* QR Code for sender URL (mobile scan)
* One-click share link
* Dark / Light theme toggle
* Real-time graphs:

  * Bandwidth
  * FPS
* Stream recording (local storage)

---

# 🧠 Architecture Notes

## Backend (FastAPI)

* Separate routes for each module:

  * `/server-settings`
  * `/network-info`
  * `/security-log`
  * `/vault`
  * `/support`

## Frontend (React)

* Modular components per section
* State management for real-time updates
* WebSocket integration for live stats

---

# ✅ End of Document
