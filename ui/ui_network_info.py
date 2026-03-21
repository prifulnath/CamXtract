import customtkinter as ctk

BG_PANEL   = "#0e0e0e"
BG_CARD    = "#1a1919"
GREEN      = "#3fff8b"
TEXT       = "#ffffff"
TEXT_DIM   = "#adaaaa"
GRAY       = "#494847"

class NetworkInfoFrame(ctk.CTkFrame):
    def __init__(self, master, app_ref, *args, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, corner_radius=0, *args, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        header.grid(row=0, column=0, padx=28, pady=(24, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        ctk.CTkLabel(titles, text="\uE774  NETWORK TOPOLOGY", font=("Segoe UI", 22, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(titles, text="Telemetry Engine // Live Data Feed", font=("Segoe UI", 11), text_color=TEXT_DIM).pack(anchor="w")

        sections = ctk.CTkFrame(self, fg_color="transparent")
        sections.grid(row=1, column=0, padx=28, pady=20, sticky="nsew")
        sections.grid_columnconfigure((0, 1, 2), weight=1)

        self._build_card(sections, 0, 0, "Basic Configuration", "Current assigned local network properties.")
        self._build_card(sections, 0, 1, "Connection Health", "Latency and packet drop evaluations.")
        self._build_card(sections, 0, 2, "Active Ports & Protocols", "8000/TCP, 8000/UDP, WebSocket mappings.")

        # Advanced routing card spanning 3 columns
        adv = ctk.CTkFrame(sections, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        adv.grid(row=1, column=0, columnspan=3, pady=(0, 16), sticky="ew")
        adv.grid_columnconfigure((0, 1, 2, 3), weight=1)
        ctk.CTkLabel(adv, text="\uE8C0  Device Discovery & Advanced Routing Engine", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(row=0, column=0, columnspan=4, sticky="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(adv, text="Real-time analysis of NAT traversal and relay infrastructure for secure P2P encryption.", font=("Segoe UI", 11), text_color=TEXT_DIM).grid(row=1, column=0, columnspan=4, sticky="w", padx=20, pady=(0, 20))
        
        self._stat(adv, 2, 0, "NAT Type", "CONE (TYPE 2)")
        self._stat(adv, 2, 1, "STUN Status", "REACHABLE")
        self._stat(adv, 2, 2, "TURN Relay", "INACTIVE")
        self._stat(adv, 2, 3, "Encryption", "AES-256-GCM")

    def _build_card(self, parent, row, col, title, desc):
        pad_x = (0, 8) if col == 0 else ((8, 0) if col == 2 else (4, 4))
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        card.grid(row=row, column=col, padx=pad_x, pady=(0, 16), sticky="nsew")
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 15, "bold"), text_color=TEXT).pack(anchor="w", padx=16, pady=(16, 5))
        ctk.CTkLabel(card, text=desc, font=("Segoe UI", 11), text_color=TEXT_DIM, wraplength=220, justify="left").pack(anchor="w", padx=16, pady=(0, 16))

    def _stat(self, parent, row, col, lbl, val):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=col, padx=20, pady=(0, 20), sticky="w")
        border = ctk.CTkFrame(f, fg_color=GREEN, width=3, height=1, bg_color="transparent")
        border.pack(side="left", fill="y", pady=2)
        inner = ctk.CTkFrame(f, fg_color="transparent")
        inner.pack(padx=12, anchor="w")
        ctk.CTkLabel(inner, text=lbl.upper(), font=("Space Grotesk", 10, "bold"), text_color=TEXT_DIM).pack(anchor="w")
        ctk.CTkLabel(inner, text=val, font=("Space Grotesk", 14, "bold"), text_color=TEXT).pack(anchor="w")
