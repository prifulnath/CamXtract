import customtkinter as ctk

BG_PANEL   = "#0e0e0e"
BG_CARD    = "#1a1919"
BG_STATS   = "#131313"
GREEN      = "#3fff8b"
GREEN_DIM  = "#24f07e"
TEXT       = "#ffffff"
TEXT_DIM   = "#adaaaa"
GRAY       = "#494847"

class ServerSettingsFrame(ctk.CTkFrame):
    def __init__(self, master, app_ref, *args, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, corner_radius=0, *args, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        header.grid(row=0, column=0, padx=28, pady=(24, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        ctk.CTkLabel(titles, text="\uE713  System Parameters", font=("Segoe UI", 22, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(titles, text="Adjust core server engine behavior and peripheral streaming logic.", font=("Segoe UI", 11), text_color=TEXT_DIM).pack(anchor="w")

        # Sections
        sections = ctk.CTkFrame(self, fg_color="transparent")
        sections.grid(row=1, column=0, padx=28, pady=20, sticky="nsew")
        sections.grid_columnconfigure((0, 1), weight=1)

        self._build_card(sections, 0, 0, "Basic Controls", "Port bindings, host IP, and basic server toggles.")
        self._build_card(sections, 0, 1, "Performance", "Thread count, buffer size, and optimization flags.")
        self._build_card(sections, 1, 0, "Camera & Stream Settings", "Resolution, framerate, and hardware encoder selection.")
        self._build_card(sections, 1, 1, "Streaming Behavior", "Bitrate limits, latency modes, and quality scaling.")

    def _build_card(self, parent, row, col, title, desc):
        pad_x = (0, 8) if col == 0 else (8, 0)
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        card.grid(row=row, column=col, padx=pad_x, pady=(0, 16), sticky="nsew")
        ctk.CTkLabel(card, text=title, font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(anchor="w", padx=20, pady=(20, 5))
        ctk.CTkLabel(card, text=desc, font=("Segoe UI", 11), text_color=TEXT_DIM, wraplength=250, justify="left").pack(anchor="w", padx=20, pady=(0, 20))
