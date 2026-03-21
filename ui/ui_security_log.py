import customtkinter as ctk

BG_PANEL   = "#0e0e0e"
BG_CARD    = "#1a1919"
RED        = "#9f0519"
TEXT       = "#ffffff"
TEXT_DIM   = "#adaaaa"
GRAY       = "#494847"

class SecurityLogFrame(ctk.CTkFrame):
    def __init__(self, master, app_ref, *args, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, corner_radius=0, *args, **kwargs)
        self.grid_columnconfigure(0, weight=1)

        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        header.grid(row=0, column=0, padx=28, pady=(24, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        ctk.CTkLabel(titles, text="\uE72E  Security Log Analysis", font=("Segoe UI", 22, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(titles, text="Real-time threat monitoring and access protocols", font=("Segoe UI", 11), text_color=TEXT_DIM).pack(anchor="w")

        # Threats
        threats = ctk.CTkFrame(self, fg_color="transparent")
        threats.grid(row=1, column=0, padx=28, pady=20, sticky="ew")
        ctk.CTkLabel(threats, text="Active Threats", font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(anchor="w", pady=(0, 10))

        self._threat_card(threats, "Unauthorized Access Attempt", "IP: 192.168.1.104", "Detected: 2m ago \u2022 Location: Beijing, CN")
        self._threat_card(threats, "Brute Force Warning", "Multiple failed logins (Admin)", "Detected: 14m ago \u2022 Origin: VPN Node #14")
        self._threat_card(threats, "Suspicious IP Pattern", "IP: 45.2.118.9", "Detected: 1h ago \u2022 Status: Monitored", is_critical=False)

    def _threat_card(self, parent, title, subtitle, meta, is_critical=True):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=4, border_width=1, border_color=RED if is_critical else GRAY)
        card.pack(fill="x", pady=4)
        left = ctk.CTkFrame(card, fg_color="transparent")
        left.pack(side="left", padx=16, pady=12)
        ctk.CTkLabel(left, text=title, font=("Segoe UI", 14, "bold"), text_color="#ff716c" if is_critical else TEXT).pack(anchor="w")
        ctk.CTkLabel(left, text=subtitle, font=("Segoe UI", 12), text_color=TEXT_DIM).pack(anchor="w")
        
        right = ctk.CTkFrame(card, fg_color="transparent")
        right.pack(side="right", padx=16, pady=12)
        ctk.CTkLabel(right, text=meta, font=("Segoe UI", 11), text_color=TEXT_DIM).pack(anchor="e")
