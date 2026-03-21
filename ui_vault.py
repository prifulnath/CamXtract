import customtkinter as ctk

BG_PANEL   = "#0e0e0e"
BG_CARD    = "#1a1919"
GREEN      = "#3fff8b"
TEXT       = "#ffffff"
TEXT_DIM   = "#adaaaa"
GRAY       = "#494847"

class VaultFrame(ctk.CTkFrame):
    def __init__(self, master, app_ref, *args, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, corner_radius=0, *args, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        header.grid(row=0, column=0, padx=28, pady=(24, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        ctk.CTkLabel(titles, text="\uE72E  System Vault", font=("Segoe UI", 22, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(titles, text="Encrypted storage for core camera credentials, network tokens, and SSL certificates.", font=("Segoe UI", 11), text_color=TEXT_DIM).pack(anchor="w")

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, padx=28, pady=20, sticky="nsew")
        content.grid_columnconfigure(0, weight=2)
        content.grid_columnconfigure(1, weight=3)

        # Left Column (Status & Features)
        left = ctk.CTkFrame(content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        
        status_card = ctk.CTkFrame(left, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        status_card.pack(fill="x", pady=(0, 16))
        ctk.CTkLabel(status_card, text="Vault Status", font=("Segoe UI", 14, "bold"), text_color=TEXT).pack(anchor="w", padx=16, pady=(16, 5))
        ctk.CTkLabel(status_card, text="\uE73E LOCKED", font=("Segoe UI", 16, "bold"), text_color=GREEN).pack(anchor="w", padx=16)
        ctk.CTkLabel(status_card, text="Last breach check: 2m ago", font=("Segoe UI", 11), text_color=TEXT_DIM).pack(anchor="w", padx=16, pady=(5, 16))

        feats_card = ctk.CTkFrame(left, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        feats_card.pack(fill="x")
        ctk.CTkLabel(feats_card, text="Active Features", font=("Segoe UI", 14, "bold"), text_color=TEXT).pack(anchor="w", padx=16, pady=(16, 10))
        self._feat(feats_card, "Auto-Encryption", "AES-256-GCM enforced")
        self._feat(feats_card, "Masked View", "Default state: Redacted")
        self._feat(feats_card, "Rotation System", "Next: 14 days remaining")

        # Right Column (Roles)
        right = ctk.CTkFrame(content, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        right.grid(row=0, column=1, sticky="nsew")
        ctk.CTkLabel(right, text="Access Roles", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(anchor="w", padx=20, pady=(20, 10))
        
        roles = [
            ("Main_Node_SSL_Cert", "SSL/TLS Certificate"),
            ("Cloud_Storage_API_V2", "REST API Key"),
            ("WebRTC_TURN_Auth", "TURN/STUN Creds"),
            ("Push_Notify_JWT", "Security Token")
        ]
        for role, desc in roles:
            row_frame = ctk.CTkFrame(right, fg_color="transparent")
            row_frame.pack(fill="x", padx=20, pady=8)
            ctk.CTkLabel(row_frame, text="\uE8D7", font=("Segoe MDL2 Assets", 16), text_color=GREEN).pack(side="left", padx=(0, 10))
            ctk.CTkLabel(row_frame, text=desc, font=("Segoe UI", 12, "bold"), text_color=TEXT).pack(side="left")
            ctk.CTkLabel(row_frame, text=role, font=("Courier New", 12), text_color=TEXT_DIM).pack(side="right")
        
        ctk.CTkLabel(right, text="Showing 4 of 4 SECURE ENTITIES", font=("Segoe UI", 10), text_color=TEXT_DIM).pack(pady=20)

    def _feat(self, parent, title, desc):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=16, pady=(0, 12))
        ctk.CTkLabel(row, text=title, font=("Segoe UI", 12, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(row, text=desc, font=("Segoe UI", 11), text_color=TEXT_DIM).pack(anchor="w")
