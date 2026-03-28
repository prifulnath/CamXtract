"""
ui_camera_controls.py
─────────────────────
Camera Controls Panel — CamXtract
Provides:
  • Live remote controls (zoom, torch, exposure, resolution, FPS, flip)
    sent over WebSocket as camera_control messages to the active sender.
  • Save / Load / Reset camera profile via the /api/camera-config REST endpoint.
  • Codec preference selection.
"""
import threading
import json
import ssl
import time
import socket

import customtkinter as ctk

try:
    import requests as _requests
    _REQUESTS_OK = True
except ImportError:
    _REQUESTS_OK = False

try:
    import websocket as _wslib      # websocket-client package
    _WS_OK = True
except ImportError:
    _WS_OK = False

# ── Theme ──────────────────────────────────────────────────────────────────────
BG_PANEL   = "#0e0e0e"
BG_CARD    = "#1a1919"
BG_CARD_HI = "#201f1f"
BG_INPUT   = "#131313"
GREEN      = "#3fff8b"
GREEN_TXT  = "#005d2c"
TEXT       = "#ffffff"
TEXT_DIM   = "#adaaaa"
OUTLINE    = "#262626"
ACCENT     = "#60d4ff"


def _get_port() -> int:
    try:
        with open("camxtract_config.json", "r", encoding="utf-8") as fh:
            cfg = json.load(fh)
        return int(cfg.get("PORT ALLOCATION", 8000))
    except Exception:
        return 8000


def _api_base() -> str:
    return f"https://127.0.0.1:{_get_port()}/api"


def _ws_url() -> str:
    port = _get_port()
    return f"wss://127.0.0.1:{port}/ws"


# ── Shared WebSocket sender (background thread) ──────────────────────────────

class _GUIWebSocket:
    """Maintains a persistent WSS connection as a GUI client for camera_control messages."""

    def __init__(self):
        self._ws = None
        self._thread = None
        self._stop = threading.Event()
        self._connected = False

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self):
        while not self._stop.is_set():
            try:
                if not _WS_OK:
                    time.sleep(5)
                    continue
                ssl_ctx = ssl.create_default_context()
                ssl_ctx.check_hostname = False
                ssl_ctx.verify_mode = ssl.CERT_NONE

                self._ws = _wslib.WebSocket(sslopt={"context": ssl_ctx})
                self._ws.connect(_ws_url())
                self._ws.send(json.dumps({"type": "register_gui"}))
                self._connected = True

                while not self._stop.is_set():
                    try:
                        self._ws.ping()
                        time.sleep(4)
                    except Exception:
                        break

            except Exception:
                pass
            finally:
                self._connected = False
                try:
                    self._ws and self._ws.close()
                except Exception:
                    pass
            time.sleep(3)  # retry delay

    def send_control(self, action: str, value):
        if not self._connected or not self._ws:
            return
        try:
            self._ws.send(json.dumps({"type": "camera_control", "action": action, "value": value}))
        except Exception:
            self._connected = False

    def stop(self):
        self._stop.set()


_gui_ws = _GUIWebSocket()


# ── Panel ──────────────────────────────────────────────────────────────────────

class CameraControlsFrame(ctk.CTkFrame):

    def __init__(self, master, app_ref, *args, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, corner_radius=0, *args, **kwargs)
        self.app_ref = app_ref
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._cam_config = {}   # cached from server
        self._torch_on = False
        self._status_var = ctk.StringVar(value="")

        self._build_header()
        self._build_body()

        # Launch the background WS client
        _gui_ws.start()

        # Load config from server (non-blocking)
        threading.Thread(target=self._fetch_config, daemon=True).start()

    # ── Header ────────────────────────────────────────────────────────────────

    def _build_header(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.grid(row=0, column=0, padx=28, pady=(24, 0), sticky="ew")
        hdr.grid_columnconfigure(0, weight=1)

        titles = ctk.CTkFrame(hdr, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(titles, text="Camera Controls",
                     font=("Segoe UI", 28, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(titles, text="Remote camera control & profile management.",
                     font=("Segoe UI", 12), text_color=TEXT_DIM).pack(anchor="w")

        btns = ctk.CTkFrame(hdr, fg_color="transparent")
        btns.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(btns, text="💾  Save Profile", width=140, height=36,
                      fg_color=GREEN, text_color=GREEN_TXT, hover_color="#13ea79",
                      font=("Segoe UI", 11, "bold"),
                      command=self._save_profile).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btns, text="📂  Load Profile", width=130, height=36,
                      fg_color="transparent", text_color=TEXT_DIM,
                      border_width=1, border_color=OUTLINE, hover_color=BG_CARD_HI,
                      font=("Segoe UI", 11, "bold"),
                      command=self._load_profile).pack(side="left", padx=(0, 8))
        ctk.CTkButton(btns, text="↺  Reset Defaults", width=140, height=36,
                      fg_color="transparent", text_color=TEXT_DIM,
                      border_width=1, border_color=OUTLINE, hover_color=BG_CARD_HI,
                      font=("Segoe UI", 11, "bold"),
                      command=self._reset_defaults).pack(side="left")

    # ── Body ──────────────────────────────────────────────────────────────────

    def _build_body(self):
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.grid(row=1, column=0, padx=28, pady=20, sticky="nsew")
        scroll.grid_columnconfigure((0, 1), weight=1)

        # ── Card 1: Live Camera Remote ────────────────────────────────────────
        remote = self._card(scroll, 0, 0, "\uE714", "LIVE REMOTE CONTROLS")

        # Flip
        flip_row = ctk.CTkFrame(remote, fg_color="transparent")
        flip_row.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkLabel(flip_row, text="Flip Camera", font=("Segoe UI", 12, "bold"), text_color=TEXT).pack(side="left")
        ctk.CTkButton(flip_row, text="🔄  Flip", width=110, height=34,
                      fg_color=BG_INPUT, text_color=TEXT, border_width=1, border_color=OUTLINE,
                      hover_color=BG_CARD_HI, font=("Segoe UI", 11, "bold"),
                      command=lambda: _gui_ws.send_control("flip", None)).pack(side="right")

        # Torch
        torch_row = ctk.CTkFrame(remote, fg_color="transparent")
        torch_row.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkLabel(torch_row, text="Torch / Flash", font=("Segoe UI", 12, "bold"), text_color=TEXT).pack(side="left")
        self._torch_btn = ctk.CTkButton(torch_row, text="🔦  OFF", width=110, height=34,
                                         fg_color=BG_INPUT, text_color=TEXT_DIM,
                                         border_width=1, border_color=OUTLINE,
                                         hover_color=BG_CARD_HI, font=("Segoe UI", 11, "bold"),
                                         command=self._toggle_torch)
        self._torch_btn.pack(side="right")

        ctk.CTkFrame(remote, fg_color=OUTLINE, height=1).pack(fill="x", padx=20, pady=8)

        # Zoom slider
        self._zoom_lbl = self._slider_row(
            remote, "Zoom", "1.0×", 1.0, 10.0, 0.1, 1.0,
            lambda v: self._on_slider("zoom", v, self._zoom_lbl, lambda x: f"{x:.1f}×")
        )

        # Exposure slider
        self._exp_lbl = self._slider_row(
            remote, "Exposure Compensation", "0.0", -3.0, 3.0, 0.1, 0.0,
            lambda v: self._on_slider("exposure", v, self._exp_lbl, lambda x: f"{'+' if x>=0 else ''}{x:.1f}")
        )

        ctk.CTkFrame(remote, fg_color=OUTLINE, height=1).pack(fill="x", padx=20, pady=8)

        # Resolution dropdown
        res_row = ctk.CTkFrame(remote, fg_color="transparent")
        res_row.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(res_row, text="Resolution", font=("Segoe UI", 10, "bold"), text_color=TEXT_DIM).pack(anchor="w", pady=(0, 4))
        self._res_menu = ctk.CTkOptionMenu(
            res_row,
            values=["1920x1080 (1080p FHD)", "2560x1440 (1440p QHD)",
                    "3840x2160 (4K UHD)", "1280x720 (720p HD)", "854x480 (480p)"],
            fg_color=BG_INPUT, button_color=BG_INPUT, button_hover_color=OUTLINE,
            dropdown_fg_color=BG_INPUT, dropdown_text_color=TEXT, text_color=TEXT,
            font=("Segoe UI", 12), corner_radius=4,
            command=self._on_resolution_change
        )
        self._res_menu.pack(fill="x")

        # FPS dropdown
        fps_row = ctk.CTkFrame(remote, fg_color="transparent")
        fps_row.pack(fill="x", padx=20, pady=(0, 12))
        ctk.CTkLabel(fps_row, text="Frame Rate", font=("Segoe UI", 10, "bold"), text_color=TEXT_DIM).pack(anchor="w", pady=(0, 4))
        self._fps_menu = ctk.CTkOptionMenu(
            fps_row,
            values=["24 fps", "30 fps", "60 fps"],
            fg_color=BG_INPUT, button_color=BG_INPUT, button_hover_color=OUTLINE,
            dropdown_fg_color=BG_INPUT, dropdown_text_color=TEXT, text_color=TEXT,
            font=("Segoe UI", 12), corner_radius=4,
            command=self._on_fps_change
        )
        self._fps_menu.set("30 fps")
        self._fps_menu.pack(fill="x")

        ctk.CTkFrame(remote, fg_color="transparent", height=12).pack()

        # ── Card 2: Encoding Settings ─────────────────────────────────────────
        enc = self._card(scroll, 0, 1, "\uE945", "ENCODING & CODEC")

        # Codec preference
        codec_row = ctk.CTkFrame(enc, fg_color="transparent")
        codec_row.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkLabel(codec_row, text="Codec Preference",
                     font=("Segoe UI", 10, "bold"), text_color=TEXT_DIM).pack(anchor="w", pady=(0, 4))
        self._codec_menu = ctk.CTkOptionMenu(
            codec_row,
            values=["VP9 (Best Quality)", "H264 (Best Compatibility)", "VP8 (Legacy)", "auto (Browser Default)"],
            fg_color=BG_INPUT, button_color=BG_INPUT, button_hover_color=OUTLINE,
            dropdown_fg_color=BG_INPUT, dropdown_text_color=TEXT, text_color=TEXT,
            font=("Segoe UI", 12), corner_radius=4
        )
        self._codec_menu.pack(fill="x")

        # Max Bitrate slider
        bitrate_row = ctk.CTkFrame(enc, fg_color="transparent")
        bitrate_row.pack(fill="x", padx=20, pady=(0, 16))
        lbl_hdr = ctk.CTkFrame(bitrate_row, fg_color="transparent")
        lbl_hdr.pack(fill="x")
        ctk.CTkLabel(lbl_hdr, text="Max Bitrate", font=("Segoe UI", 10, "bold"), text_color=TEXT_DIM).pack(side="left")
        self._bitrate_lbl = ctk.CTkLabel(lbl_hdr, text="8 Mbps", font=("Segoe UI", 12, "bold"), text_color=ACCENT)
        self._bitrate_lbl.pack(side="right")
        self._bitrate_slider = ctk.CTkSlider(
            bitrate_row, from_=1, to=20, number_of_steps=19,
            button_color=ACCENT, fg_color=OUTLINE, progress_color=ACCENT,
            command=lambda v: self._bitrate_lbl.configure(text=f"{int(v)} Mbps")
        )
        self._bitrate_slider.set(8)
        self._bitrate_slider.pack(fill="x", pady=(8, 0))

        # Adaptive Bitrate switch
        abr_row = ctk.CTkFrame(enc, fg_color="transparent")
        abr_row.pack(fill="x", padx=20, pady=(0, 16))
        txt = ctk.CTkFrame(abr_row, fg_color="transparent")
        txt.pack(side="left")
        ctk.CTkLabel(txt, text="Adaptive Bitrate (ABR)", font=("Segoe UI", 12, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(txt, text="Auto-scale bitrate based on network conditions",
                     font=("Segoe UI", 10), text_color=TEXT_DIM).pack(anchor="w")
        self._abr_switch = ctk.CTkSwitch(abr_row, text="", progress_color=GREEN, button_color=TEXT, button_hover_color=TEXT)
        self._abr_switch.select()
        self._abr_switch.pack(side="right")

        # Use Ideal constraints switch
        ideal_row = ctk.CTkFrame(enc, fg_color="transparent")
        ideal_row.pack(fill="x", padx=20, pady=(0, 16))
        txt2 = ctk.CTkFrame(ideal_row, fg_color="transparent")
        txt2.pack(side="left")
        ctk.CTkLabel(txt2, text="Use 'ideal' Constraints", font=("Segoe UI", 12, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(txt2, text="Allow browser to choose closest supported resolution",
                     font=("Segoe UI", 10), text_color=TEXT_DIM).pack(anchor="w")
        self._ideal_switch = ctk.CTkSwitch(ideal_row, text="", progress_color=GREEN, button_color=TEXT, button_hover_color=TEXT)
        self._ideal_switch.select()
        self._ideal_switch.pack(side="right")

        ctk.CTkFrame(enc, fg_color="transparent", height=12).pack()

        # ── Status bar ────────────────────────────────────────────────────────
        status_bar = ctk.CTkFrame(self, fg_color="#0d0d0d", border_width=1, border_color=OUTLINE)
        status_bar.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 0))
        ctk.CTkLabel(status_bar, textvariable=self._status_var,
                     font=("Segoe UI", 10), text_color=TEXT_DIM).pack(padx=20, pady=6, anchor="w")

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _card(self, parent, row, col, icon, title):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=8)
        card.grid(row=row, column=col,
                  padx=(0, 8) if col == 0 else (8, 0),
                  pady=(0, 16), sticky="nsew")
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(anchor="w", padx=20, pady=(20, 16))
        ctk.CTkLabel(hdr, text=icon, font=("Segoe MDL2 Assets", 18), text_color=GREEN).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(hdr, text=title, font=("Segoe UI", 12, "bold"), text_color=TEXT).pack(side="left")
        return card

    def _slider_row(self, parent, label, init_text, from_, to, step, init_val, command):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 12))
        hdr = ctk.CTkFrame(row, fg_color="transparent")
        hdr.pack(fill="x")
        ctk.CTkLabel(hdr, text=label, font=("Segoe UI", 10, "bold"), text_color=TEXT_DIM).pack(side="left")
        lbl = ctk.CTkLabel(hdr, text=init_text, font=("Segoe UI", 12, "bold"), text_color=ACCENT)
        lbl.pack(side="right")
        slider = ctk.CTkSlider(row, from_=from_, to=to, number_of_steps=int((to - from_) / step),
                               button_color=ACCENT, fg_color=OUTLINE, progress_color=ACCENT,
                               command=command)
        slider.set(init_val)
        slider.pack(fill="x", pady=(8, 0))
        return lbl

    def _on_slider(self, action, value, label_widget, formatter):
        label_widget.configure(text=formatter(value))
        _gui_ws.send_control(action, round(float(value), 2))

    def _toggle_torch(self):
        self._torch_on = not self._torch_on
        if self._torch_on:
            self._torch_btn.configure(text="🔦  ON", text_color=GREEN, border_color=GREEN)
        else:
            self._torch_btn.configure(text="🔦  OFF", text_color=TEXT_DIM, border_color=OUTLINE)
        _gui_ws.send_control("torch", self._torch_on)

    def _on_resolution_change(self, display_val: str):
        # Extract raw resolution string e.g. "1920x1080"
        raw = display_val.split(" ")[0]
        _gui_ws.send_control("resolution", raw)
        self._set_status(f"Resolution changed → {raw}")

    def _on_fps_change(self, display_val: str):
        raw = int(display_val.split(" ")[0])
        _gui_ws.send_control("fps", raw)
        self._set_status(f"FPS changed → {raw}")

    def _set_status(self, msg: str):
        self._status_var.set(f"  {msg}")

    # ── Profile save / load / reset ──────────────────────────────────────────

    def _build_camera_payload(self) -> dict:
        res_raw = self._res_menu.get().split(" ")[0]
        fps_raw = int(self._fps_menu.get().split(" ")[0])
        codec_raw = self._codec_menu.get().split(" ")[0]
        return {
            "resolution": res_raw,
            "preferred_fps": fps_raw,
            "codec_preference": codec_raw,
            "use_ideal": bool(self._ideal_switch.get()),
            "fallback_resolutions": ["1280x720", "854x480"],
            "zoom": 1.0,
            "exposure_compensation": 0.0,
            "torch": self._torch_on,
            "facing_mode": "environment",
            "max_bitrate_mbps": int(self._bitrate_slider.get())
        }

    def _save_profile(self):
        if not _REQUESTS_OK:
            self._set_status("⚠ requests package not installed. Run: pip install requests")
            return
        threading.Thread(target=self._do_save, daemon=True).start()

    def _do_save(self):
        try:
            payload = self._build_camera_payload()
            r = _requests.put(f"{_api_base()}/camera-config",
                              json=payload, verify=False, timeout=5)
            if r.ok:
                self.after(0, lambda: self._set_status("✅ Camera profile saved."))
            else:
                self.after(0, lambda: self._set_status(f"⚠ Save failed: {r.status_code}"))
        except Exception as e:
            self.after(0, lambda: self._set_status(f"⚠ {e}"))

    def _load_profile(self):
        if not _REQUESTS_OK:
            self._set_status("⚠ requests package not installed.")
            return
        threading.Thread(target=self._do_load, daemon=True).start()

    def _do_load(self):
        try:
            r = _requests.get(f"{_api_base()}/camera-config", verify=False, timeout=5)
            if r.ok:
                cfg = r.json()
                self.after(0, lambda: self._populate(cfg))
                self.after(0, lambda: self._set_status("✅ Camera profile loaded."))
            else:
                self.after(0, lambda: self._set_status(f"⚠ Load failed: {r.status_code}"))
        except Exception as e:
            self.after(0, lambda: self._set_status(f"⚠ {e}"))

    def _populate(self, cfg: dict):
        # Resolution
        res = cfg.get("resolution", "1920x1080")
        for item in self._res_menu.cget("values"):
            if item.startswith(res):
                self._res_menu.set(item)
                break
        # FPS
        fps = cfg.get("preferred_fps", 30)
        self._fps_menu.set(f"{fps} fps")
        # Codec
        codec = cfg.get("codec_preference", "VP9")
        for item in self._codec_menu.cget("values"):
            if item.startswith(codec):
                self._codec_menu.set(item)
                break
        # Bitrate
        self._bitrate_slider.set(cfg.get("max_bitrate_mbps", 8))
        self._bitrate_lbl.configure(text=f"{cfg.get('max_bitrate_mbps', 8)} Mbps")
        # Ideal
        if cfg.get("use_ideal", True):
            self._ideal_switch.select()
        else:
            self._ideal_switch.deselect()
        # Torch
        self._torch_on = cfg.get("torch", False)
        self._torch_btn.configure(
            text="🔦  ON" if self._torch_on else "🔦  OFF",
            text_color=GREEN if self._torch_on else TEXT_DIM,
            border_color=GREEN if self._torch_on else OUTLINE
        )

    def _reset_defaults(self):
        if not _REQUESTS_OK:
            self._set_status("⚠ requests package not installed.")
            return
        threading.Thread(target=self._do_reset, daemon=True).start()

    def _do_reset(self):
        try:
            r = _requests.post(f"{_api_base()}/camera-config/reset", verify=False, timeout=5)
            if r.ok:
                cfg = r.json().get("config", {})
                self.after(0, lambda: self._populate(cfg))
                self.after(0, lambda: self._set_status("✅ Camera profile reset to defaults."))
            else:
                self.after(0, lambda: self._set_status(f"⚠ Reset failed: {r.status_code}"))
        except Exception as e:
            self.after(0, lambda: self._set_status(f"⚠ {e}"))

    def _fetch_config(self):
        """Load config on panel first open."""
        if not _REQUESTS_OK:
            return
        time.sleep(1)  # give server a moment if auto-starting
        self._do_load()
