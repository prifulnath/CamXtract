import customtkinter as ctk
import webbrowser
import platform
import os
from tkinter import filedialog

BG_PANEL   = "#0e0e0e"
BG_CARD    = "#1a1919"   # surface-container
BG_LOW     = "#131313"   # surface-container-low
BG_HIGHEST = "#262626"   # surface-container-highest
BG_LOWEST  = "#000000"   # surface-container-lowest
GREEN      = "#3fff8b"
GREEN_DIM  = "#24f07e"
GREEN_TEXT = "#005d2c"
TEXT       = "#ffffff"
TEXT_DIM   = "#adaaaa"
GRAY       = "#494847"

class SupportFrame(ctk.CTkFrame):
    def __init__(self, master, app_ref, *args, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, corner_radius=0, *args, **kwargs)
        self.app_ref = app_ref
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=0)

        # Header Section
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=28, pady=(24, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        
        ctk.CTkLabel(header, text="System Support", font=("Space Grotesk", 36, "bold"), text_color=TEXT).pack(anchor="w", pady=(0, 4))
        ctk.CTkLabel(header, text="Diagnostics and technical assistance console for CamXtract visual intelligence infrastructure.", font=("Space Grotesk", 14), text_color=TEXT_DIM).pack(anchor="w")

        # Bento Grid Configuration
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, padx=28, pady=(12, 16), sticky="nsew")
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        # Left Column (col-span-8 equivalent)
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        
        # Troubleshooting Tools
        tools_card = ctk.CTkFrame(left, fg_color=BG_CARD, corner_radius=8)
        tools_card.pack(fill="x", pady=(0, 12))
        
        tools_header = ctk.CTkFrame(tools_card, fg_color="transparent")
        tools_header.pack(fill="x", padx=20, pady=(16, 10))
        ctk.CTkLabel(tools_header, text="TROUBLESHOOTING TOOLS", font=("Space Grotesk", 11, "bold"), text_color=GREEN).pack(side="left")
        
        ready_badge = ctk.CTkFrame(tools_header, fg_color=BG_HIGHEST, corner_radius=4)
        ready_badge.pack(side="right")
        ctk.CTkLabel(ready_badge, text="READY", font=("Courier New", 10, "bold"), text_color=TEXT_DIM).pack(padx=6, pady=2)
        
        tools_grid = ctk.CTkFrame(tools_card, fg_color="transparent")
        tools_grid.pack(fill="x", padx=20, pady=(0, 16))
        tools_grid.grid_columnconfigure((0, 1, 2), weight=1)
        
        self._tool_btn(tools_grid, 0, "\uE89A", "TEST CAMERA",    "Open sender URL in browser",   self._test_camera)
        self._tool_btn(tools_grid, 1, "\uE8AD", "NETWORK INFO",   "Switch to Network Info panel", self._go_network)
        self._tool_btn(tools_grid, 2, "\uE8CA", "STREAM REFRESH", "Restart the CamXtract server",       self._stream_refresh)

        # Technical Documentation
        docs_card = ctk.CTkFrame(left, fg_color=BG_LOW, corner_radius=8)
        docs_card.pack(fill="both", expand=True)
        
        ctk.CTkLabel(docs_card, text="TECHNICAL DOCUMENTATION", font=("Space Grotesk", 11, "bold"), text_color=TEXT_DIM).pack(anchor="w", padx=20, pady=(16, 10))
        
        self._doc(docs_card, "\uE8A5", "CamXtract Deployment Guide", "Step-by-step camera provisioning and local setup.")
        self._doc(docs_card, "\uE8D7", "SSL & Security Handshake", "Resolving common certificate and HTTPS warnings.")
        self._doc(docs_card, "\uE90F", "Hardware Fixes", "Manual focus adjustment and IR filter troubleshooting.")

        # Right Column (col-span-4 equivalent)
        right = ctk.CTkFrame(content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        # Debug Protocol
        debug_card = ctk.CTkFrame(right, fg_color=BG_HIGHEST, corner_radius=8)
        debug_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(debug_card, text="DEBUG PROTOCOL", font=("Space Grotesk", 11, "bold"), text_color=GREEN).pack(anchor="w", padx=20, pady=(16, 10))

        console_box = ctk.CTkFrame(debug_card, fg_color=BG_LOWEST, corner_radius=4)
        console_box.pack(fill="x", padx=20, pady=(0, 10))
        log_text = "[SYS_INFO]: OK\n[NET_STACK]: SECURE\n[KERN_V]: 2.4.0-S\n[LAST_ERR]: NONE"
        ctk.CTkLabel(console_box, text=log_text, font=("Courier New", 10), text_color="#2cefbc", justify="left").pack(anchor="w", padx=12, pady=12)
        
        ctk.CTkButton(debug_card, text="\uE896  EXPORT SYSTEM LOGS", font=("Space Grotesk", 10, "bold"), fg_color=GREEN, text_color=GREEN_TEXT, hover_color=GREEN_DIM, height=36, corner_radius=4, command=self._export_logs).pack(fill="x", padx=20, pady=(0, 8))
        ctk.CTkButton(debug_card, text="\uE81C  CORE DUMP", font=("Space Grotesk", 10, "bold"), fg_color="transparent", text_color=GREEN, hover_color=BG_LOW, border_width=1, border_color=GRAY, height=36, corner_radius=4, command=self._core_dump).pack(fill="x", padx=20, pady=(0, 16))

        # Support Channels
        channels_card = ctk.CTkFrame(right, fg_color=BG_CARD, corner_radius=8)
        channels_card.pack(fill="both", expand=True)

        ctk.CTkLabel(channels_card, text="SUPPORT CHANNELS", font=("Space Grotesk", 11, "bold"), text_color=TEXT_DIM).pack(anchor="w", padx=20, pady=(16, 10))
        
        self._channel(channels_card, "\uE715", "Email Support", "Response in 24h", "mailto:prifulnath@gmail.com")
        self._channel(channels_card, "\uE8EF", "GitHub Issues", "Community tracker", "https://github.com/prifulnath/CamXtract/issues")
        self._channel(channels_card, "\uE9CE", "Public FAQ", "Searchable database", "https://github.com/prifulnath/CamXtract/blob/main/FAQ.md")

        # ── Copyright Footer ──────────────────────────────────────────────────
        foot = ctk.CTkFrame(self, fg_color="#080808", corner_radius=0,
                            border_width=1, border_color="#1a1a1a")
        foot.grid(row=2, column=0, sticky="ew")
        foot.grid_columnconfigure(1, weight=1)

        status_lbl = ctk.CTkFrame(foot, fg_color="transparent")
        status_lbl.grid(row=0, column=0, padx=20, pady=8, sticky="w")
        ctk.CTkLabel(status_lbl, text="\u25CF ", font=("Segoe UI", 9),
                     text_color=GREEN).pack(side="left")
        ctk.CTkLabel(status_lbl, text="CamXtract SYSTEM STATUS: ",
                     font=("Space Grotesk", 9, "bold"), text_color=TEXT_DIM).pack(side="left")
        ctk.CTkLabel(status_lbl, text="OPERATIONAL",
                     font=("Space Grotesk", 9, "bold"), text_color=GREEN).pack(side="left")

        ctk.CTkLabel(foot, text="\u00A9 2026 MalluCodeX / ALL RIGHTS RESERVED",
                     font=("Space Grotesk", 8), text_color="#444444"
                     ).grid(row=0, column=1, padx=20, pady=8, sticky="e")

    def _tool_btn(self, parent, col, icon, title, desc, command=None, obs_mode=False):
        last_col = 2
        pad_x = (0, 8) if col == 0 else ((8, 0) if col == last_col else (8, 8))
        icon_color = "#b48bff" if obs_mode else GREEN
        frame = ctk.CTkFrame(parent, fg_color=BG_LOW, corner_radius=6, height=110)
        frame.grid(row=0, column=col, sticky="nsew", padx=pad_x)
        frame.grid_propagate(False)
        frame.grid_columnconfigure(0, weight=1)
        inner = ctk.CTkFrame(frame, fg_color="transparent")
        inner.pack(anchor="w", padx=16, pady=14)
        icon_lbl   = ctk.CTkLabel(inner, text=icon,  font=("Segoe MDL2 Assets", 22), text_color=icon_color)
        icon_lbl.pack(anchor="w", pady=(0, 8))
        title_lbl  = ctk.CTkLabel(inner, text=title, font=("Space Grotesk", 12, "bold"), text_color=TEXT)
        title_lbl.pack(anchor="w")
        desc_lbl   = ctk.CTkLabel(inner, text=desc,  font=("Space Grotesk", 11), text_color=TEXT_DIM)
        desc_lbl.pack(anchor="w")
        def on_enter(e): frame.configure(fg_color=BG_HIGHEST)
        def on_leave(e): frame.configure(fg_color=BG_LOW)
        for w in [frame, inner, icon_lbl, title_lbl, desc_lbl]:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            if command:
                w.bind("<Button-1>", lambda e, c=command: c())

    def _doc(self, parent, icon, title, desc, command=None, obs_mode=False):
        row = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=6)
        row.pack(fill="x", padx=16, pady=(0, 8))
        
        left_box = ctk.CTkFrame(row, fg_color="transparent")
        left_box.pack(side="left", padx=14, pady=12)
        
        accent = "#b48bff" if obs_mode else TEXT_DIM
        icon_lbl = ctk.CTkLabel(left_box, text=icon, font=("Segoe MDL2 Assets", 20), text_color=accent)
        icon_lbl.pack(side="left", padx=(0, 16))
        
        text_box = ctk.CTkFrame(left_box, fg_color="transparent")
        text_box.pack(side="left")
        title_lbl = ctk.CTkLabel(text_box, text=title, font=("Space Grotesk", 12, "bold"), text_color=TEXT)
        title_lbl.pack(anchor="w")
        desc_lbl = ctk.CTkLabel(text_box, text=desc, font=("Space Grotesk", 11), text_color=TEXT_DIM)
        desc_lbl.pack(anchor="w")
        
        chevron_icon = "\uE8A7" if command else "\uE76C"
        chevron = ctk.CTkLabel(row, text=chevron_icon, font=("Segoe MDL2 Assets", 14), text_color=TEXT_DIM)
        chevron.pack(side="right", padx=16)
        
        hover_color = "#b48bff" if obs_mode else GREEN
        def on_enter(e):
            row.configure(fg_color=BG_HIGHEST)
            icon_lbl.configure(text_color=hover_color)
        def on_leave(e):
            row.configure(fg_color=BG_PANEL)
            icon_lbl.configure(text_color=accent)
            
        for w in [row, left_box, icon_lbl, text_box, title_lbl, desc_lbl, chevron]:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            if command:
                w.bind("<Button-1>", lambda e, c=command: c())




    def _test_camera(self):
        console = self.app_ref.frames.get("Console")
        if console and self.app_ref._server_running:
            ip = self.app_ref.ip
            port = console._server_port
            webbrowser.open(f"https://{ip}:{port}/sender.html")
        else:
            webbrowser.open("about:blank")

    def _go_network(self):
        self.app_ref.show_frame("Network Info")
        self.app_ref.sidebar.set_active("Network Info")

    def _stream_refresh(self):
        console = self.app_ref.frames.get("Console")
        if console:
            if console._server_running:
                console.stop_server()
                self.after(2000, console.start_server)
            else:
                console.start_server()

    def _export_logs(self):
        console = self.app_ref.frames.get("Console")
        if not console:
            return
        content = console.log_box.get("1.0", "end")
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text Files", "*.txt")], title="Export System Logs"
        )
        if path:
            with open(path, "w") as f:
                f.write(f"CamXtract \u2014 System Log Export\n{'='*40}\n{content}")

    def _core_dump(self):
        info = platform.uname()
        content = (
            f"CamXtract \u2014 Core Dump\n{'='*40}\n"
            f"System:    {info.system}\n"
            f"Node:      {info.node}\n"
            f"Release:   {info.release}\n"
            f"Version:   {info.version}\n"
            f"Machine:   {info.machine}\n"
            f"Processor: {info.processor}\n"
        )
        path = filedialog.asksaveasfilename(
            defaultextension=".txt", filetypes=[("Text Files", "*.txt")], title="Save Core Dump"
        )
        if path:
            with open(path, "w") as f:
                f.write(content)

    def _channel(self, parent, icon, title, desc, link):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 10))
        
        icon_box = ctk.CTkFrame(row, fg_color=BG_HIGHEST, corner_radius=6, width=40, height=40)
        icon_box.pack(side="left", padx=(0, 16))
        icon_box.pack_propagate(False)
        icon_lbl = ctk.CTkLabel(icon_box, text=icon, font=("Segoe MDL2 Assets", 16), text_color=TEXT_DIM)
        icon_lbl.place(relx=0.5, rely=0.5, anchor="center")
        
        text_box = ctk.CTkFrame(row, fg_color="transparent")
        text_box.pack(side="left")
        title_lbl = ctk.CTkLabel(text_box, text=title, font=("Space Grotesk", 12, "bold"), text_color=TEXT)
        title_lbl.pack(anchor="w")
        desc_lbl = ctk.CTkLabel(text_box, text=desc, font=("Space Grotesk", 11), text_color=TEXT_DIM)
        desc_lbl.pack(anchor="w")
        
        def on_enter(e):
            icon_lbl.configure(text_color=GREEN)
            title_lbl.configure(text_color=GREEN)
        def on_leave(e):
            icon_lbl.configure(text_color=TEXT_DIM)
            title_lbl.configure(text_color=TEXT)
        def on_click(e):
            webbrowser.open(link)
            
        for w in [row, icon_box, icon_lbl, text_box, title_lbl, desc_lbl]:
            w.bind("<Enter>", on_enter)
            w.bind("<Leave>", on_leave)
            w.bind("<Button-1>", on_click)
