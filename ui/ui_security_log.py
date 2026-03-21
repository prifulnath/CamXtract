import customtkinter as ctk

BG_PANEL   = "#0e0e0e"
BG_CARD    = "#1a1919"
BG_CARD_H  = "#262626"
BG_CARD_L  = "#131313"
BG_ALERT   = "#250c0e"
BG_GLASS   = "#1d1d1d" 
GREEN      = "#3fff8b"
GREEN_TXT  = "#005d2c"
GREEN_DIM  = "#24f07e"
CYAN       = "#45fec9"
CYAN_DIM   = "#2cefbc"
TEXT       = "#ffffff"
TEXT_DIM   = "#adaaaa"
GRAY       = "#494847"
RED        = "#ff716c"
RED_DIM    = "#d7383b"
ERR_CONT   = "#9f0519"

class SecurityLogFrame(ctk.CTkFrame):
    def __init__(self, master, app_ref, *args, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, corner_radius=0, *args, **kwargs)
        self.app_ref = app_ref
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._build_header()
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, padx=24, pady=16, sticky="nsew")
        content.grid_columnconfigure(0, weight=1, minsize=300)
        content.grid_columnconfigure(1, weight=2, minsize=600)
        content.grid_rowconfigure(0, weight=1)
        
        self._build_left_col(content)
        self._build_right_col(content)
        
        self._build_footer()
        
    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=24, pady=(20, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        
        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w")
        
        h_title = ctk.CTkFrame(titles, fg_color="transparent")
        h_title.pack(anchor="w")
        ctk.CTkLabel(h_title, text="SECURITY LOG ", font=("Space Grotesk", 26, "bold"), text_color=TEXT).pack(side="left")
        ctk.CTkLabel(h_title, text="ANALYSIS", font=("Space Grotesk", 26, "bold"), text_color=GREEN).pack(side="left")
        
        ctk.CTkLabel(titles, text="REAL-TIME THREAT MONITORING AND ACCESS PROTOCOLS", font=("Space Grotesk", 11, "bold"), text_color=TEXT_DIM).pack(anchor="w")
        
        btns = ctk.CTkFrame(header, fg_color="transparent")
        btns.grid(row=0, column=1, sticky="e")
        
        btn_refresh = ctk.CTkFrame(btns, fg_color=BG_CARD_H, border_width=1, border_color=GRAY, corner_radius=6, height=36)
        btn_refresh.pack(side="left", padx=(0, 10))
        btn_refresh.pack_propagate(False)
        ctk.CTkLabel(btn_refresh, text="\uE72C   REFRESH", font=("Space Grotesk", 10, "bold"), text_color=TEXT).pack(padx=16, pady=8)
        
        btn_dl = ctk.CTkFrame(btns, fg_color=GREEN, corner_radius=6, height=36)
        btn_dl.pack(side="left")
        btn_dl.pack_propagate(False)
        ctk.CTkLabel(btn_dl, text="\uE896   DOWNLOAD LOGS", font=("Space Grotesk", 10, "bold"), text_color=GREEN_TXT).pack(padx=16, pady=8)

    def _build_left_col(self, parent):
        left = ctk.CTkFrame(parent, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 16))
        
        th_head = ctk.CTkFrame(left, fg_color="transparent")
        th_head.pack(fill="x", padx=4, pady=(0, 14))
        ctk.CTkLabel(th_head, text="\u25CF ", font=("Segoe UI", 12), text_color=GREEN).pack(side="left")
        ctk.CTkLabel(th_head, text="ACTIVE THREATS", font=("Space Grotesk", 10, "bold"), text_color=GREEN).pack(side="left", padx=4)
        
        # 1. Critical Alert (Red)
        self._alert_card(left, True, "\uE730", RED, "UNAUTHORIZED ACCESS ATTEMPT", "IP: 192.168.1.104", "DETECTED: 2M AGO \u2022 LOCATION: BEIJING, CN")
        # 2. Warning Alert (Gray bg, no left border)
        self._alert_card(left, False, "\uE916", GREEN_DIM, "BRUTE FORCE WARNING", "Multiple failed logins (Admin)", "DETECTED: 14M AGO \u2022 ORIGIN: VPN NODE #14")
        # 3. Info Alert
        self._alert_card(left, False, "\uE9A2", CYAN_DIM, "SUSPICIOUS IP PATTERN", "IP: 45.2.118.9", "DETECTED: 1H AGO \u2022 STATUS: MONITORED")
        
        self._ssl_card(left)
        
    def _alert_card(self, parent, is_crit, icon, icon_col, title, sub, meta):
        bg_col = BG_ALERT if is_crit else BG_CARD
        border_col = ERR_CONT if is_crit else GRAY
        card = ctk.CTkFrame(parent, fg_color=bg_col, corner_radius=6, border_width=1, border_color=border_col)
        card.pack(fill="x", pady=(0, 12))
        
        if is_crit:
            accent = ctk.CTkFrame(card, width=4, fg_color=RED, corner_radius=0)
            accent.pack(side="left", fill="y")
            
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=14, pady=14)
        
        ctk.CTkLabel(inner, text=icon, font=("Segoe MDL2 Assets", 18), text_color=icon_col).pack(side="left", anchor="n", padx=(0, 12))
        
        txt_frm = ctk.CTkFrame(inner, fg_color="transparent")
        txt_frm.pack(side="left", fill="x", expand=True)
        
        ctk.CTkLabel(txt_frm, text=title, font=("Space Grotesk", 10, "bold"), text_color=RED if is_crit else TEXT).pack(anchor="w")
        ctk.CTkLabel(txt_frm, text=sub, font=("Courier New", 12, "bold") if "IP" in sub else ("Space Grotesk", 12), text_color=TEXT).pack(anchor="w", pady=(2, 6))
        ctk.CTkLabel(txt_frm, text=meta, font=("Space Grotesk", 8, "bold"), text_color=TEXT_DIM).pack(anchor="w")

    def _ssl_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=BG_GLASS, corner_radius=10, border_width=1, border_color=GRAY)
        card.pack(fill="x", pady=(16, 0))
        card.grid_columnconfigure(1, weight=1)
        
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.grid(row=0, column=0, columnspan=2, sticky="ew", padx=16, pady=16)
        ctk.CTkLabel(head, text="SSL CERTIFICATE", font=("Space Grotesk", 10, "bold"), text_color=TEXT).pack(side="left")
        badge = ctk.CTkFrame(head, fg_color="#12251a", corner_radius=10)
        badge.pack(side="right")
        ctk.CTkLabel(badge, text="ACTIVE", font=("Space Grotesk", 8, "bold"), text_color=GREEN).pack(padx=8, pady=2)
        
        self._ssl_row(card, 1, "ISSUER", "Let's Encrypt R3", TEXT)
        self._ssl_row(card, 2, "PROTOCOL", "TLS 1.3", TEXT)
        self._ssl_row(card, 3, "EXPIRY", "2024-11-20 (22 Days)", RED)
        
        bar = ctk.CTkFrame(card, fg_color=BG_CARD_H, height=6, corner_radius=3)
        bar.grid(row=4, column=0, columnspan=2, sticky="ew", padx=16, pady=(16, 20))
        bar.grid_propagate(False)
        ctk.CTkFrame(bar, fg_color=GREEN, height=6, corner_radius=3).place(relwidth=0.8, rely=0)

    def _ssl_row(self, parent, r, k, v, color):
        ctk.CTkLabel(parent, text=k, font=("Space Grotesk", 9), text_color=TEXT_DIM).grid(row=r, column=0, sticky="w", padx=16, pady=4)
        ctk.CTkLabel(parent, text=v, font=("Courier New", 11, "bold") if "Lett" not in v else ("Space Grotesk", 11), text_color=color).grid(row=r, column=1, sticky="e", padx=16, pady=4)

    def _build_right_col(self, parent):
        right = ctk.CTkFrame(parent, fg_color=BG_CARD_L, corner_radius=12, border_width=1, border_color=GRAY)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)
        
        # Tabs
        tabs = ctk.CTkFrame(right, fg_color="transparent")
        tabs.grid(row=0, column=0, sticky="ew", padx=20, pady=0)
        
        # Frame underneath tabs to act as border border-outline-variant/10
        b_bot = ctk.CTkFrame(right, fg_color=GRAY, height=1)
        b_bot.grid(row=0, column=0, sticky="ew", pady=(40, 0))

        tab_area = ctk.CTkFrame(tabs, fg_color="transparent")
        tab_area.pack(fill="x", pady=(14, 0))
        
        t1 = ctk.CTkLabel(tab_area, text="ALL ACTIVITY", font=("Space Grotesk", 10, "bold"), text_color=GREEN)
        t1.pack(side="left", padx=(0, 16))
        ctk.CTkFrame(tab_area, fg_color=GREEN, height=2, width=80).place(x=0, y=20)
        
        ctk.CTkLabel(tab_area, text="FAILURES", font=("Space Grotesk", 10, "bold"), text_color=TEXT_DIM).pack(side="left", padx=16)
        ctk.CTkLabel(tab_area, text="SSH", font=("Space Grotesk", 10, "bold"), text_color=TEXT_DIM).pack(side="left", padx=16)
        
        dot = ctk.CTkFrame(tab_area, fg_color="transparent")
        dot.pack(side="right")
        ctk.CTkLabel(dot, text="\u25CF ", font=("Segoe UI", 8), text_color=GREEN).pack(side="left")
        ctk.CTkLabel(dot, text="LIVE_STREAM_ENABLED", font=("Courier New", 8, "bold"), text_color=TEXT_DIM).pack(side="left")
        
        # Logs
        self.log_box = ctk.CTkTextbox(right, fg_color="transparent", text_color=TEXT_DIM, font=("Courier New", 12))
        self.log_box.grid(row=1, column=0, sticky="nsew", padx=16, pady=16)
        self._populate_logs()
        
        # Bottom Buttons
        b_top = ctk.CTkFrame(right, fg_color=GRAY, height=1)
        b_top.grid(row=2, column=0, sticky="ew")
        
        bot_btns = ctk.CTkFrame(right, fg_color="transparent")
        bot_btns.grid(row=3, column=0, sticky="ew", padx=20, pady=20)
        bot_btns.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self._action_btn(bot_btns, 0, RED, "\uE735", "BLOCK IP", True)
        self._action_btn(bot_btns, 1, GREEN, "\uE73A", "ALLOWLIST")
        self._action_btn(bot_btns, 2, CYAN, "\uE756", "CLI ACCESS")
        self._action_btn(bot_btns, 3, TEXT, "\uE74D", "CLEAR LOGS", False, True)

    def _action_btn(self, parent, col, color, icon, label, b_left=False, b_right=False):
        f = ctk.CTkFrame(parent, fg_color=BG_CARD_H, corner_radius=6, border_width=1, border_color=GRAY)
        pL = 0 if b_left else 6
        pR = 0 if b_right else 6
        f.grid(row=0, column=col, sticky="nsew", padx=(pL, pR))
        
        inner = ctk.CTkFrame(f, fg_color="transparent")
        inner.pack(expand=True, pady=16)
        ctk.CTkLabel(inner, text=icon, font=("Segoe MDL2 Assets", 18), text_color=color).pack()
        ctk.CTkLabel(inner, text=label, font=("Space Grotesk", 9, "bold"), text_color=TEXT_DIM).pack(pady=(4, 0))

    def _populate_logs(self):
        self.log_box.configure(state="normal")
        self.log_box.tag_config("green", foreground=GREEN)
        self.log_box.tag_config("red", foreground=RED)
        self.log_box.tag_config("cyan", foreground=CYAN)
        
        # HTML design specifically uses these tags per log line
        L = [
            ("[14:22:01]", "AUTH_SUCCESS", GREEN, "User ", "ADMIN_SRV", GREEN, " logged in via WEB_UI", "172.16.0.45"),
            ("[14:21:44]", "AUTH_FAILED", RED_DIM, "Invalid credentials for user ", "ROOT", RED, " (Attempt 3/5)", "192.168.1.104"),
            ("[14:18:32]", "SYS_CONFIG", GREEN, "Firewall rules updated: ", "BLOCK_LIST_SYNC", CYAN, " completed", "INTERNAL"),
            ("[14:15:10]", "CONN_INFO", CYAN_DIM, "New session established via SSH: ", "terminal_agent_09", TEXT_DIM, "", "10.0.4.21"),
            ("[14:10:05]", "AUTH_FAILED", RED_DIM, "Invalid credentials for user ", "ROOT", RED, " (Attempt 2/5)", "192.168.1.104"),
            ("[14:05:59]", "SSL_RENEW", GREEN_DIM, "Automated cert renewal check: ", "SUCCESS", GREEN, "", "SYSTEM"),
            ("[13:58:22]", "CONN_DROP", CYAN_DIM, "Inbound connection dropped from ", "45.2.118.9", RED, " (Geofence violation)", "GATEWAY_01"),
            ("[13:45:01]", "HEARTBEAT", TEXT_DIM, "System status: ", "OPTIMAL", GREEN_DIM, "", "INTERNAL"),
            ("[13:30:00]", "HEARTBEAT", TEXT_DIM, "System status: ", "OPTIMAL", GREEN_DIM, "", "INTERNAL")
        ]
        
        for p1, t_lbl, t_col, m1, m2, m2_col, m3, sys in L:
            self.log_box.insert("end", p1 + "  ")
            
            # Label
            self.log_box.insert("end", t_lbl, t_lbl+"_T")
            self.log_box.tag_config(t_lbl+"_T", foreground=t_col)
            padding = " " * max(1, 14 - len(t_lbl))
            self.log_box.insert("end", padding)
            
            # Msg pt 1
            self.log_box.insert("end", m1, "TXT")
            # Msg pt 2
            tk = m2+"_T"
            self.log_box.insert("end", m2, tk)
            self.log_box.tag_config(tk, foreground=m2_col)
            # Msg pt 3
            self.log_box.insert("end", m3 + " ", "TXT")
            
            # Align system code
            curr_line_len = len(p1) + 2 + 14 + len(m1) + len(m2) + len(m3) + 1
            sys_pad = " " * max(1, 85 - curr_line_len - len(sys))
            
            self.log_box.insert("end", sys_pad + sys + "\n\n", "SYS")
            
        self.log_box.tag_config("TXT", foreground=TEXT)
        self.log_box.tag_config("SYS", foreground=TEXT_DIM)
        self.log_box.configure(state="disabled")

    def _build_footer(self):
        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.grid(row=2, column=0, padx=24, pady=(0, 24), sticky="ew")
        foot.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        self._footer_card(foot, 0, "TOTAL INBOUND", "12.4K", "+2%", GREEN)
        self._footer_card(foot, 1, "BLOCKED ATTACKS", "842", "+12%", RED)
        self._footer_card(foot, 2, "FAILED LOGINS", "29", "STABLE", TEXT_DIM)
        self._footer_card(foot, 3, "SYSTEM UPTIME", "99.98%", "OPTIMAL", GREEN)

    def _footer_card(self, parent, col, title, main_val, sub_val, sub_color):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color=GRAY)
        pad_l = 0 if col==0 else 8
        pad_r = 0 if col==3 else 8
        card.grid(row=0, column=col, sticky="nsew", padx=(pad_l, pad_r))
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(anchor="w", padx=20, pady=20)
        
        ctk.CTkLabel(inner, text=title, font=("Space Grotesk", 9, "bold"), text_color=TEXT_DIM).pack(anchor="w", pady=(0, 6))
        val_row = ctk.CTkFrame(inner, fg_color="transparent")
        val_row.pack(anchor="w")
        ctk.CTkLabel(val_row, text=main_val, font=("Space Grotesk", 22, "bold"), text_color=TEXT).pack(side="left")
        ctk.CTkLabel(val_row, text=" "+sub_val, font=("Courier New", 10, "bold") if "STABLE" not in sub_val and "OPTIMAL" not in sub_val else ("Space Grotesk", 10, "bold"), text_color=sub_color).pack(side="left", pady=(4, 0))
