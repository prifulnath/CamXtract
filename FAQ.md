# MCX Cam — Frequently Asked Questions (FAQ)

*Version 0.0.1 · MalluCodeX*

---

## 🚀 Getting Started

**Q: What is MCX Cam?**  
MCX Cam is a desktop application that turns any mobile device into a live webcam, streaming video directly to your computer over your local WiFi network using WebRTC — no internet or cloud required.

**Q: What devices are supported?**  
- **Sender (Camera):** Any smartphone with a modern browser (Chrome, Safari, Firefox)
- **Viewer:** Windows PC running the MCX Cam desktop app, or any browser on the same network
- **OS:** Windows 10/11 (for the `.exe`); the web viewer works on any OS

**Q: Do I need an internet connection?**  
No. MCX Cam works entirely on your local WiFi network. The only internet access is for STUN server lookups (to establish the peer connection), which are very lightweight.

---

## 🔐 SSL & Certificate Issues

**Q: Why does the browser say "Not Private" or "Your connection is not secure"?**  
MCX Cam generates a self-signed SSL certificate for your local IP address. This is required for camera access on mobile browsers (especially iOS Safari). The warning is expected — click **Advanced → Proceed** (Chrome) or **Show Details → Visit this website** (Safari).

**Q: How do I regenerate the SSL certificate?**  
If your computer's IP address changes (e.g., after reconnecting to WiFi):
1. Delete `key.pem` and `cert.pem` from the folder containing `MCX_Cam.exe`
2. Restart the app — fresh certificates are generated automatically

**Q: The camera feed isn't loading on iOS Safari.**  
Ensure you have accepted the self-signed certificate on iOS by visiting the server URL directly in Safari and tapping **Visit this website**. iOS requires this trust step before any camera stream can load.

---

## 📡 Streaming & Connection

**Q: The viewer shows a black screen or no feed.**  
Try these steps:
1. Make sure the **sender** has connected first (camera icon visible in browser)
2. Reload the viewer page
3. Check that both devices are on the **same WiFi network**
4. Click **STREAM REFRESH** in the Support panel to restart the server

**Q: How many viewers can watch simultaneously?**  
The current WebRTC architecture is a **1-to-1** peer connection. For multiple viewers, an SFU (Selective Forwarding Unit) would be needed — this is planned for a future release.

**Q: The stream is laggy or choppy.**  
- Move devices closer to the WiFi router
- Avoid using 2.4GHz (prefer 5GHz if available)
- Lower the resolution on the sender side
- Close other bandwidth-heavy applications

**Q: Can I stream audio too?**  
Not in v0.0.1. Audio streaming is planned for a future release.

---

## 🖥️ Desktop App (MCX Cam GUI)

**Q: The app takes a long time to open on first launch.**  
The first launch extracts the PyInstaller bundle to a temporary folder (one-time process). Subsequent launches are significantly faster. The app also shows a splash screen while panels load.

**Q: Why does clicking "Camera Monitor" take a few seconds the first time?**  
The Camera Monitor panel loads the Microsoft Edge WebView2 runtime (`.NET CLR`) lazily — only when you first navigate to it. This is intentional to keep startup time fast.

**Q: The minimize button doesn't work.**  
This was a known bug in earlier builds (v0.0.1 fixes it). The custom title bar uses a Win32 API call to minimize instead of the standard Tkinter method.

**Q: Where is the configuration saved?**  
Settings (server name, port, sliders, toggles) are saved to `mcx_config.json` in the same directory as the `.exe`. Delete this file to reset to defaults.

**Q: Can I use MCX Cam with OBS Studio?**  
Yes. Start the MCX Cam server, then add a **Browser Source** in OBS using the OBS URL shown in the Console panel (`https://<IP>:<PORT>/obs.html`).

---

## 🔧 Troubleshooting

**Q: "Error loading Support" or other panel load errors.**  
This usually means a Python dependency is missing or an update broke compatibility. Try re-installing from `requirements.txt`:
```powershell
pip install -r requirements.txt
```

**Q: The server won't start — "No module named ..."**  
If running from source: ensure your virtual environment is active (`.venv\Scripts\Activate.ps1`) and all dependencies are installed.

**Q: How do I export the system log?**  
In the **Support** panel, click **EXPORT SYSTEM LOGS** — you'll be prompted to save a `.txt` file with the full console history.

**Q: The SSL Vault shows "Not configured".**  
This means `cert.pem` and `key.pem` don't exist yet. Start the server at least once — it generates the certificates automatically.

---

## 📦 Build & Distribution

**Q: How do I build my own `.exe`?**  
See the [README build instructions](README.md#building-the-standalone-exe). Use the `version_info.txt` for embedded Windows metadata.

**Q: Can I run MCX Cam on macOS or Linux?**  
The `.exe` is Windows-only. Running from source (`python gui.py`) may work on macOS/Linux but the Camera Monitor (Edge WebView2) is Windows-only. Other panels should work cross-platform.

---

## 📬 Contact & Support

- **GitHub Issues:** [github.com/prifulnath/MCX_Cam/issues](https://github.com/prifulnath/MCX_Cam/issues)
- **Email:** prifulnath@gmail.com

---

*© 2026 MalluCodeX. All rights reserved.*
