import customtkinter as ctk

# Colors
BG_SIDEBAR = "#0a120e"
GREEN = "#3fff8b"
GREEN_DIM = "#13ea79"
GREEN_SIDE = "#16281f"
GREEN_TEXT = "#005d2c"
TEXT_DIM = "#adaaaa"

class MenuFrame(ctk.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master, fg_color=BG_SIDEBAR, corner_radius=0, width=210)
        self.app_ref = app_ref
        
        self.grid(row=1, column=0, sticky="nsew")
        self.grid_propagate(False)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(7, weight=1)

        # Node badge
        badge = ctk.CTkFrame(self, fg_color="transparent")
        badge.grid(row=0, column=0, padx=14, pady=(20, 6), sticky="ew")
        badge_inner = ctk.CTkFrame(badge, fg_color="transparent")
        badge_inner.pack(padx=12, pady=8, fill="x")
        
        icon_box = ctk.CTkFrame(badge_inner, width=32, height=32, fg_color="#12251a", border_width=1, border_color="#183d26", corner_radius=2)
        icon_box.grid_propagate(False)
        icon_box.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(icon_box, text="\uE968", font=("Segoe MDL2 Assets", 16), text_color=GREEN).place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(badge_inner, fg_color="transparent")
        info.pack(side="left", fill="y", pady=(2, 0))
        self.app_ref.node_badge_label = ctk.CTkLabel(info, text="CamXtract-01", font=("Segoe UI", 14, "bold"), text_color=GREEN, anchor="w", height=18)
        self.app_ref.node_badge_label.pack(anchor="w", pady=0)
        ctk.CTkLabel(info, text="V0.0.1", font=("Segoe UI", 9), text_color=TEXT_DIM, anchor="w", height=12).pack(anchor="w", pady=(0, 0), padx=(1, 0))

        # Nav items
        nav_items = [
            ("\uE756", "Console",          True),
            ("\uE713", "Server Settings",   False),
            ("\uE714", "Camera Controls",   False),
            ("\uE774", "Network Info",      False),
            ("\uE91C", "Security Log",      False),
            ("\uE722", "Camera Monitor",    False),
        ]
        
        self.app_ref.nav_buttons = {}
        for i, (icon, label, active) in enumerate(nav_items):
            row_frame = ctk.CTkFrame(self, fg_color=GREEN_SIDE if active else "transparent", corner_radius=0)
            row_frame.grid(row=i + 1, column=0, pady=0, sticky="ew")
            row_frame.bind("<Button-1>", lambda e, n=label: self.app_ref.show_frame(n))
            
            indicator = ctk.CTkFrame(row_frame, width=3, height=0)
            indicator.pack(side="left", fill="y")
            indicator.configure(fg_color=GREEN if active else "transparent")
                
            text_color = GREEN if active else TEXT_DIM
            lbl = ctk.CTkLabel(row_frame, text=f"  {icon}   {label}", font=("Segoe UI", 12, "bold"), text_color=text_color, anchor="w")
            lbl.pack(side="left", padx=20, pady=10)
            lbl.bind("<Button-1>", lambda e, n=label: self.app_ref.show_frame(n))
            
            self.app_ref.nav_buttons[label] = {"frame": row_frame, "label": lbl, "indicator": indicator}

        # Spacer fills remaining space (no visual widget needed)
        self.grid_rowconfigure(7, weight=1)

        # Keep a hidden dummy so gui.py's deploy_btn.configure() doesn't crash
        self.deploy_btn = ctk.CTkButton(self, text="", fg_color="transparent", height=0)

        # Horizontal separator above bottom nav
        sep = ctk.CTkFrame(self, fg_color="#2a4035", height=2, corner_radius=0)
        sep.grid(row=8, column=0, sticky="ew", padx=14, pady=(6, 2))

        # Bottom nav
        for i, (icon, label) in enumerate([("\uEBD3", "Vault"), ("\uE939", "Support")]):
            row_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
            row_frame.grid(row=9 + i, column=0, padx=0, pady=0, sticky="ew")
            row_frame.bind("<Button-1>", lambda e, n=label: self.app_ref.show_frame(n))

            indicator = ctk.CTkFrame(row_frame, width=3, height=0)
            indicator.pack(side="left", fill="y")
            indicator.configure(fg_color="transparent")

            lbl = ctk.CTkLabel(row_frame, text=f"  {icon}   {label}",
                               font=("Segoe UI", 12, "bold"), text_color=TEXT_DIM, anchor="w")
            lbl.pack(side="left", padx=20, pady=10)
            lbl.bind("<Button-1>", lambda e, n=label: self.app_ref.show_frame(n))

            self.app_ref.nav_buttons[label] = {"frame": row_frame, "label": lbl, "indicator": indicator}

        # Bottom padding
        ctk.CTkFrame(self, fg_color="transparent", height=12).grid(row=11, column=0)

    def set_active(self, name):
        """Programmatically highlight a sidebar nav item."""
        for label, widgets in self.app_ref.nav_buttons.items():
            is_active = label == name
            widgets["frame"].configure(fg_color=GREEN_SIDE if is_active else "transparent")
            widgets["label"].configure(text_color=GREEN if is_active else TEXT_DIM)
            widgets["indicator"].configure(fg_color=GREEN if is_active else "transparent")
