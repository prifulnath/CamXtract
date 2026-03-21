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
        self.grid_rowconfigure(6, weight=1)

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
        self.app_ref.node_badge_label = ctk.CTkLabel(info, text="MCX-01", font=("Segoe UI", 14, "bold"), text_color=GREEN, anchor="w", height=18)
        self.app_ref.node_badge_label.pack(anchor="w", pady=0)
        ctk.CTkLabel(info, text="ACTIVE NODE", font=("Segoe UI", 9), text_color=TEXT_DIM, anchor="w", height=12).pack(anchor="w", pady=(0, 0), padx=(1, 0))

        # Nav items
        nav_items = [
            ("\uE756", "Console",        True),
            ("\uE713", "Server Settings", False),
            ("\uE774", "Network Info",   False),
            ("\uE72E", "Security Log",   False),
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

        # Spacer
        ctk.CTkLabel(self, text="", fg_color="transparent").grid(row=6, column=0, sticky="ew")

        # Deploy button
        deploy_btn = ctk.CTkButton(
            self, text="\uE945  DEPLOY NODE",
            font=("Segoe UI", 12, "bold"),
            fg_color=GREEN, text_color=GREEN_TEXT,
            hover_color=GREEN_DIM, corner_radius=2, height=44,
            command=self.app_ref._update_server_name
        )
        deploy_btn.grid(row=7, column=0, padx=16, pady=(0, 16), sticky="ew")
        
        # Save deploy btn ref for mapping in gui.py
        self.deploy_btn = deploy_btn

        # Bottom nav
        for i, (icon, label) in enumerate([("\uE72E", "Vault"), ("\uE897", "Support")]):
            row_frame = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
            row_frame.grid(row=8 + i, column=0, padx=0, pady=0, sticky="ew")
            row_frame.bind("<Button-1>", lambda e, n=label: self.app_ref.show_frame(n))
            
            indicator = ctk.CTkFrame(row_frame, width=3, height=0)
            indicator.pack(side="left", fill="y")
            indicator.configure(fg_color="transparent")

            lbl = ctk.CTkLabel(row_frame, text=f"   {icon}   {label}", font=("Segoe UI", 11, "bold"), text_color=TEXT_DIM, anchor="w")
            lbl.pack(side="left", padx=16, pady=8)
            lbl.bind("<Button-1>", lambda e, n=label: self.app_ref.show_frame(n))
            
            self.app_ref.nav_buttons[label] = {"frame": row_frame, "label": lbl, "indicator": indicator}
