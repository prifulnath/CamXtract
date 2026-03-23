import customtkinter as ctk

BG_PANEL   = "#0e0e0e"
BG_CARD    = "#1a1919"
BG_CARD_HI = "#201f1f"
BG_INPUT   = "#131313"
GREEN      = "#3fff8b"
GREEN_TXT  = "#005d2c"
TEXT       = "#ffffff"
TEXT_DIM   = "#adaaaa"
GRAY       = "#494847"
OUTLINE_DIM= "#262626"
import json
import os

CONFIG_FILE = "mcx_config.json"

class ServerSettingsFrame(ctk.CTkFrame):
    def __init__(self, master, app_ref, *args, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, corner_radius=0, *args, **kwargs)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self.config = self._load_config()
        self.ui_elements = {}

        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=28, pady=(24, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(titles, text="System Parameters", font=("Segoe UI", 28, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(titles, text="Adjust core server engine behavior and peripheral streaming logic.", font=("Segoe UI", 12), text_color=TEXT_DIM).pack(anchor="w")

        btns = ctk.CTkFrame(header, fg_color="transparent")
        btns.grid(row=0, column=1, sticky="e")
        ctk.CTkButton(btns, text="DISCARD", fg_color="transparent", text_color=TEXT_DIM,
                      border_width=1, border_color=GRAY, hover_color=BG_CARD_HI, width=100, height=36,
                      font=("Segoe UI", 11, "bold")).pack(side="left", padx=(0, 10))
        self.deploy_btn = ctk.CTkButton(btns, text="DEPLOY CONFIGURATION", fg_color=GREEN, text_color=GREEN_TXT,
                      hover_color="#13ea79", width=180, height=36,
                      font=("Segoe UI", 11, "bold"))
        self.deploy_btn.pack(side="left")

        # Scrollable Content Area
        scroll_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_area.grid(row=1, column=0, padx=28, pady=20, sticky="nsew")
        scroll_area.grid_columnconfigure((0, 1), weight=1)

        # ── 1. Basic Controls ──
        basic = ctk.CTkFrame(scroll_area, fg_color=BG_CARD, corner_radius=8)
        basic.grid(row=0, column=0, padx=(0, 8), pady=(0, 16), sticky="nsew")
        basic.grid_columnconfigure((0, 1), weight=1)

        title_frame1 = ctk.CTkFrame(basic, fg_color="transparent")
        title_frame1.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")
        ctk.CTkLabel(title_frame1, text="\uE8C0", font=("Segoe MDL2 Assets", 18), text_color=GREEN).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_frame1, text="BASIC CONTROLS", font=("Segoe UI", 12, "bold"), text_color=TEXT).pack(side="left")

        self.server_name_entry = self._build_input(basic, 1, 0, "SERVER NAME", "MCX-01")
        self.port_entry = self._build_input(basic, 1, 1, "PORT ALLOCATION", "8000")
        self._build_dropdown(basic, 2, 0, "PROTOCOL", ["Secure WebSocket (WSS)", "Standard HTTP", "UDP Blast"], span=2)
        self._build_switch(basic, 3, 0, "Auto-start Engine", "Initialize on system boot", True, span=2)

        # ── 2. Performance ──
        perf = ctk.CTkFrame(scroll_area, fg_color=BG_CARD_HI, corner_radius=8)
        perf.grid(row=0, column=1, padx=(8, 0), pady=(0, 16), sticky="nsew")
        perf.grid_columnconfigure(0, weight=1)

        title_frame2 = ctk.CTkFrame(perf, fg_color="transparent")
        title_frame2.pack(anchor="w", padx=20, pady=20)
        ctk.CTkLabel(title_frame2, text="\uE945", font=("Segoe MDL2 Assets", 18), text_color=GREEN).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_frame2, text="PERFORMANCE", font=("Segoe UI", 12, "bold"), text_color=TEXT).pack(side="left")

        self._build_switch(perf, -1, -1, "Hardware Acceleration", "Enable NVIDIA NVENC cores", True, use_pack=True)
        
        slide_frame = ctk.CTkFrame(perf, fg_color="transparent")
        slide_frame.pack(fill="x", padx=20, pady=16)
        lbl_head = ctk.CTkFrame(slide_frame, fg_color="transparent")
        lbl_head.pack(fill="x")
        ctk.CTkLabel(lbl_head, text="CPU LIMITER", font=("Segoe UI", 10, "bold"), text_color=TEXT_DIM).pack(side="left")
        _cpu_lbl = ctk.CTkLabel(lbl_head, text="75%", font=("Segoe UI", 12, "bold"), text_color=GREEN)
        _cpu_lbl.pack(side="right")
        _cpu_slider = ctk.CTkSlider(slide_frame, from_=0, to=100, number_of_steps=100,
                                    button_color=GREEN, fg_color=OUTLINE_DIM, progress_color=GREEN,
                                    command=lambda v: _cpu_lbl.configure(text=f"{int(v)}%"))
        _cpu_init = int(self.config.get("CPU LIMITER", 75))
        _cpu_slider.set(_cpu_init)
        _cpu_lbl.configure(text=f"{_cpu_init}%")
        _cpu_slider.pack(fill="x", pady=(10, 0))
        self.ui_elements["CPU LIMITER"] = _cpu_slider

        self._build_switch(perf, -1, -1, "Adaptive Bitrate", "Dynamic scaling based on congestion", False, use_pack=True)

        # ── 3. Camera & Stream Settings ──
        cam = ctk.CTkFrame(scroll_area, fg_color=BG_CARD, corner_radius=8)
        cam.grid(row=1, column=0, padx=(0, 8), pady=0, sticky="nsew")
        cam.grid_columnconfigure((0, 1), weight=1)

        title_frame3 = ctk.CTkFrame(cam, fg_color="transparent")
        title_frame3.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="w")
        ctk.CTkLabel(title_frame3, text="\uE714", font=("Segoe MDL2 Assets", 18), text_color=GREEN).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_frame3, text="CAMERA & STREAM SETTINGS", font=("Segoe UI", 12, "bold"), text_color=TEXT).pack(side="left")
        
        lbl_badge = ctk.CTkLabel(cam, text=" Active Input: Cam_01 ", font=("Segoe UI", 10, "bold"), text_color=GREEN, fg_color="#12251a", corner_radius=4)
        lbl_badge.grid(row=0, column=1, sticky="e", padx=20)

        self._build_dropdown(cam, 1, 0, "PRIMARY INPUT DEVICE", ["UltraHD Wide-Angle Core (USB-C)", "Internal System Optics", "Virtual OBS Feed"], span=2)
        self._build_dropdown(cam, 2, 0, "RESOLUTION", ["3840 x 2160", "1920 x 1080", "1280 x 720"])
        self._build_dropdown(cam, 2, 1, "FPS", ["24", "30", "60", "120"])

        # Inner stats cards
        stats_frame = ctk.CTkFrame(cam, fg_color="transparent")
        stats_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=(20, 20), sticky="ew")
        stats_frame.grid_columnconfigure((0, 1, 2), weight=1)
        self._mini_stat(stats_frame, 0, 0, "Target Bitrate", "6.5", "Mbps")
        self._mini_stat(stats_frame, 0, 1, "Codec Profile", "H.265", "Main10")
        self._mini_stat(stats_frame, 0, 2, "Color Space", "BT.2020", "HDR")

        # ── 4. Streaming Behavior ──
        stream = ctk.CTkFrame(scroll_area, fg_color=BG_CARD, corner_radius=8)
        stream.grid(row=1, column=1, padx=(8, 0), pady=0, sticky="nsew")
        
        title_frame4 = ctk.CTkFrame(stream, fg_color="transparent")
        title_frame4.pack(anchor="w", padx=20, pady=20)
        ctk.CTkLabel(title_frame4, text="\uE8C0", font=("Segoe MDL2 Assets", 18), text_color=GREEN).pack(side="left", padx=(0, 10))
        ctk.CTkLabel(title_frame4, text="STREAMING BEHAVIOR", font=("Segoe UI", 12, "bold"), text_color=TEXT).pack(side="left")

        slide_frame2 = ctk.CTkFrame(stream, fg_color="transparent")
        slide_frame2.pack(fill="x", padx=20, pady=(0, 16))
        lbl_head2 = ctk.CTkFrame(slide_frame2, fg_color="transparent")
        lbl_head2.pack(fill="x")
        ctk.CTkLabel(lbl_head2, text="MAX VIEWERS", font=("Segoe UI", 10, "bold"), text_color=TEXT_DIM).pack(side="left")
        _viewers_lbl = ctk.CTkLabel(lbl_head2, text="12", font=("Segoe UI", 12, "bold"), text_color=GREEN)
        _viewers_lbl.pack(side="right")
        _viewers_slider = ctk.CTkSlider(slide_frame2, from_=1, to=50, number_of_steps=49,
                                        button_color=GREEN, fg_color=OUTLINE_DIM, progress_color=GREEN,
                                        command=lambda v: _viewers_lbl.configure(text=str(int(v))))
        _viewers_init = int(self.config.get("MAX VIEWERS", 12))
        _viewers_slider.set(_viewers_init)
        _viewers_lbl.configure(text=str(_viewers_init))
        _viewers_slider.pack(fill="x", pady=(10, 0))
        self.ui_elements["MAX VIEWERS"] = _viewers_slider

        self._build_dropdown(stream, -1, -1, "INACTIVITY TIMEOUT", ["5 Minutes", "15 Minutes", "30 Minutes", "Never"], use_pack=True)
        self._build_switch(stream, -1, -1, "Auto-Reconnect", "Retry on network drop", True, use_pack=True)

        warning_frm = ctk.CTkFrame(stream, fg_color="transparent")
        warning_frm.pack(fill="x", padx=20, pady=20, side="bottom")
        ctk.CTkFrame(stream, height=1, fg_color=OUTLINE_DIM).pack(fill="x", padx=20, side="bottom")
        ctk.CTkLabel(warning_frm, text="\uE946   Changes to streaming behavior require a service restart.", font=("Segoe UI", 10, "italic"), text_color=TEXT_DIM).pack(anchor="w")

        # ── Footer Stats Bar ──
        footer = ctk.CTkFrame(self, fg_color="#0d0d0d", border_width=1, border_color=OUTLINE_DIM)
        footer.grid(row=2, column=0, sticky="ew", padx=28, pady=(0, 0))
        footer_inner = ctk.CTkFrame(footer, fg_color="transparent")
        footer_inner.pack(fill="x", padx=20, pady=10)

        self._footer_stat(footer_inner, "\u25CF", GREEN,     "SYSTEM STATUS", "NOMINAL")
        self._footer_stat(footer_inner, "\u25CF", GREEN,     "MEMORY LOAD",   "14%")
        self._footer_stat(footer_inner, "\u2B06", "#4a86e8", "UPLINK",        "ACTIVE [124ms]")

    def _build_input(self, parent, row, col, label, val):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=col, padx=20, pady=(0, 20), sticky="ew")
        ctk.CTkLabel(f, text=label, font=("Segoe UI", 10, "bold"), text_color=TEXT_DIM).pack(anchor="w", pady=(0, 5))
        e = ctk.CTkEntry(f, font=("Segoe UI", 14), fg_color=BG_INPUT, border_width=0, corner_radius=4, text_color=TEXT)
        e.pack(fill="x")
        
        saved_val = self.config.get(label, val)
        e.insert(0, saved_val)
        self.ui_elements[label] = e
        return e

    def _build_dropdown(self, parent, row, col, label, vals, span=1, use_pack=False):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        if use_pack:
            f.pack(fill="x", padx=20, pady=(0, 20))
        else:
            f.grid(row=row, column=col, columnspan=span, padx=20, pady=(0, 20), sticky="ew")
        ctk.CTkLabel(f, text=label, font=("Segoe UI", 10, "bold"), text_color=TEXT_DIM).pack(anchor="w", pady=(0, 5))
        opt = ctk.CTkOptionMenu(f, values=vals, font=("Segoe UI", 12), fg_color=BG_INPUT, button_color=BG_INPUT, button_hover_color=GRAY, dropdown_fg_color=BG_INPUT, dropdown_text_color=TEXT, text_color=TEXT, corner_radius=4)
        
        saved_val = self.config.get(label, vals[0])
        opt.set(saved_val if saved_val in vals else vals[0])
        opt.pack(fill="x")
        self.ui_elements[label] = opt
        return opt

    def _build_switch(self, parent, row, col, title, desc, on, span=1, use_pack=False):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        if use_pack:
            f.pack(fill="x", padx=20, pady=(0, 20))
        else:
            f.grid(row=row, column=col, columnspan=span, padx=20, pady=(0, 20), sticky="ew")
        
        text_f = ctk.CTkFrame(f, fg_color="transparent")
        text_f.pack(side="left")
        ctk.CTkLabel(text_f, text=title, font=("Segoe UI", 12, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(text_f, text=desc, font=("Segoe UI", 10), text_color=TEXT_DIM).pack(anchor="w")
        
        sw = ctk.CTkSwitch(f, text="", progress_color=GREEN, button_color=TEXT, button_hover_color=TEXT)
        
        is_on = self.config.get(title, on)
        if str(is_on).lower() in ("true", "1", "yes"): 
            sw.select()
        else: 
            sw.deselect()
            
        sw.pack(side="right")
        self.ui_elements[title] = sw
        return sw

    def _mini_stat(self, parent, row, col, title, val, unit):
        f = ctk.CTkFrame(parent, fg_color=BG_INPUT, corner_radius=4)
        f.grid(row=row, column=col, padx=(0, 8) if col < 2 else 0, sticky="ew")
        ctk.CTkLabel(f, text=title.upper(), font=("Segoe UI", 9, "bold"), text_color=TEXT_DIM).pack(anchor="w", padx=10, pady=(10, 0))
        
        val_f = ctk.CTkFrame(f, fg_color="transparent")
        val_f.pack(anchor="w", padx=10, pady=(0, 10))
        ctk.CTkLabel(val_f, text=val, font=("Space Grotesk", 18, "bold"), text_color=TEXT).pack(side="left")
        ctk.CTkLabel(val_f, text=" "+unit, font=("Segoe UI", 11), text_color=TEXT_DIM).pack(side="left", pady=(4, 0))

    def _footer_stat(self, parent, dot, dot_col, lbl, val):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.pack(side="left", padx=(0, 28))
        ctk.CTkLabel(f, text=dot + " ", font=("Segoe UI", 10), text_color=dot_col).pack(side="left")
        ctk.CTkLabel(f, text=lbl + ": ", font=("Space Grotesk", 9, "bold"), text_color=TEXT_DIM).pack(side="left")
        ctk.CTkLabel(f, text=val, font=("Space Grotesk", 9, "bold"), text_color=TEXT).pack(side="left")

    def _load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f:
                    return json.load(f)
            except:
                pass
        return {}

    def save_config(self):
        for key, widget in self.ui_elements.items():
            self.config[key] = widget.get()
            
        try:
            with open(CONFIG_FILE, "w") as f:
                json.dump(self.config, f, indent=4)
        except:
            pass
