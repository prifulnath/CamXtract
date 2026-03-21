import customtkinter as ctk
import webbrowser

BG_PANEL   = "#0e0e0e"
BG_CARD    = "#1a1919"
GREEN      = "#3fff8b"
TEXT       = "#ffffff"
TEXT_DIM   = "#adaaaa"
GRAY       = "#494847"

class SupportFrame(ctk.CTkFrame):
    def __init__(self, master, app_ref, *args, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, corner_radius=0, *args, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        header.grid(row=0, column=0, padx=28, pady=(24, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        ctk.CTkLabel(titles, text="\uE897  SYSTEM SUPPORT", font=("Segoe UI", 22, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(titles, text="Diagnostics and technical assistance console for MCX-CORE visual intelligence infrastructure.", font=("Segoe UI", 11), text_color=TEXT_DIM).pack(anchor="w")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, padx=28, pady=20, sticky="nsew")
        content.grid_columnconfigure((0, 1), weight=1)

        # Left Column: Docs & Debug
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        docs = ctk.CTkFrame(left, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        docs.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(docs, text="Technical Documentation", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(anchor="w", padx=20, pady=(20, 10))
        self._doc(docs, "MCX Deployment Guide", "Step-by-step camera provisioning and local setup.")
        self._doc(docs, "SSL & Security Handshake", "Resolving common certificate and HTTPS warnings.")
        self._doc(docs, "Hardware Fixes", "Manual focus adjustment and IR filter troubleshooting.")
        
        debug = ctk.CTkFrame(left, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        debug.pack(fill="x")
        ctk.CTkLabel(debug, text="Debug Protocol", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(anchor="w", padx=20, pady=20)

        # Right Column: Channels
        right = ctk.CTkFrame(content, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))
        ctk.CTkLabel(right, text="Support Channels", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(anchor="w", padx=20, pady=(20, 10))
        
        self._channel(right, "\uE715", "Email Support", "Response in 24h", "mailto:support@mcxcam.local")
        self._channel(right, "\uE8EF", "GitHub Issues", "Community tracker", "https://github.com/mcx/issues")
        self._channel(right, "\uE9CE", "Public FAQ", "Searchable database", "https://mcxcam.com/faq")

    def _doc(self, parent, title, desc):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 16))
        ctk.CTkLabel(row, text=title, font=("Segoe UI", 12, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(row, text=desc, font=("Segoe UI", 11), text_color=TEXT_DIM).pack(anchor="w")

    def _channel(self, parent, icon, title, desc, link):
        row = ctk.CTkFrame(parent, fg_color=BG_PANEL, corner_radius=6)
        row.pack(fill="x", padx=20, pady=(0, 12))
        
        icon_lbl = ctk.CTkLabel(row, text=icon, font=("Segoe MDL2 Assets", 20), text_color=GREEN)
        icon_lbl.pack(side="left", padx=16, pady=16)
        
        text_frame = ctk.CTkFrame(row, fg_color="transparent")
        text_frame.pack(side="left")
        ctk.CTkLabel(text_frame, text=title, font=("Segoe UI", 14, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(text_frame, text=desc, font=("Segoe UI", 11), text_color=TEXT_DIM).pack(anchor="w")
        
        launch = ctk.CTkButton(row, text="\uE8A7", width=32, height=32, font=("Segoe MDL2 Assets", 14), fg_color="transparent", hover_color=GRAY, text_color=TEXT, command=lambda: webbrowser.open(link))
        launch.pack(side="right", padx=16)
