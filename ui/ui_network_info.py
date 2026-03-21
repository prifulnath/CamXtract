import customtkinter as ctk

BG_PANEL   = "#0e0e0e"
BG_CARD    = "#1a1919"
BG_CARD_L  = "#201f1f"
BG_INPUT   = "#131313"
GREEN      = "#3fff8b"
GREEN_TXT  = "#005d2c"
TEXT       = "#ffffff"
TEXT_DIM   = "#adaaaa"
GRAY       = "#494847"
RED        = "#ff716c"
GRAY_DARK  = "#262626"

class NetworkInfoFrame(ctk.CTkFrame):
    def __init__(self, master, app_ref, *args, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, corner_radius=0, *args, **kwargs)
        self.app_ref = app_ref
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        self._build_header()
        
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, padx=28, pady=20, sticky="nsew")
        content.grid_columnconfigure((0, 1, 2), weight=1)

        self._build_basic_config(content, row=0, col=0)
        self._build_conn_health(content, row=0, col=1)

        self._build_ports(content, row=1, col=0)
        self._build_device_discovery(content, row=1, col=1)

        self._build_adv_routing(content, row=2)

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=28, pady=(24, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)
        
        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w")
        
        ctk.CTkLabel(titles, text="Network Topology", font=("Space Grotesk", 28, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(titles, text="TELEMETRY ENGINE // LIVE DATA FEED", font=("Space Grotesk", 12, "bold"), text_color=TEXT_DIM).pack(anchor="w")
        
        btns = ctk.CTkFrame(header, fg_color="transparent")
        btns.grid(row=0, column=1, sticky="e")
        
        ctk.CTkButton(btns, text="\uE72C  RE-SCAN NETWORK", font=("Space Grotesk", 11, "bold"), height=36, fg_color="transparent", border_width=1, border_color=GRAY, text_color=GREEN, hover_color=BG_CARD_L).pack(side="left", padx=(0, 12))
        ctk.CTkButton(btns, text="\uE896  EXPORT LOGS", font=("Space Grotesk", 11, "bold"), height=36, fg_color=GREEN, text_color=GREEN_TXT, hover_color="#24f07e").pack(side="left")

    def _build_basic_config(self, parent, row, col):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=4)
        card.grid(row=row, column=col, padx=(0, 12), pady=(0, 16), sticky="nsew")
        
        th_head = ctk.CTkFrame(card, fg_color="transparent")
        th_head.pack(fill="x", padx=16, pady=20)
        ctk.CTkLabel(th_head, text="\u25CF ", font=("Segoe UI", 12), text_color=GREEN).pack(side="left")
        ctk.CTkLabel(th_head, text="BASIC CONFIGURATION", font=("Space Grotesk", 10, "bold"), text_color=GREEN).pack(side="left")
        ctk.CTkLabel(th_head, text="\uE946", font=("Segoe MDL2 Assets", 18), text_color=GRAY_DARK).pack(side="right")
        
        box = ctk.CTkFrame(card, fg_color="transparent")
        box.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        self._cfg_row(box, "LOCAL IP ADDRESS", "192.168.1.104", hl=True)
        self._cfg_row(box, "PUBLIC IP ADDRESS", "45.231.12.89")
        self._cfg_row(box, "HOSTNAME", "MCX-NODE-04")
        self._cfg_row(box, "MAC ADDRESS", "00:1A:2B:3C:4D:5E")

    def _cfg_row(self, parent, k, v, hl=False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=8)
        ctk.CTkLabel(row, text=k, font=("Space Grotesk", 10), text_color=TEXT_DIM).pack(side="left")
        val_f = ctk.CTkFrame(row, fg_color=BG_INPUT if hl else "transparent", corner_radius=4)
        val_f.pack(side="right")
        ctk.CTkLabel(val_f, text=v, font=("Courier New", 12, "bold"), text_color=TEXT).pack(padx=6 if hl else 0, pady=2 if hl else 0)

    def _build_conn_health(self, parent, row, col):
        card = ctk.CTkFrame(parent, fg_color="transparent")
        card.grid(row=row, column=col, columnspan=2, padx=(12, 0), pady=(0, 16), sticky="nsew")
        card.grid_rowconfigure(1, weight=1)
        card.grid_columnconfigure((0,1,2), weight=1)
        
        th_head = ctk.CTkFrame(card, fg_color="transparent")
        th_head.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(16, 20))
        ctk.CTkLabel(th_head, text="\u25CF ", font=("Segoe UI", 12), text_color=GREEN).pack(side="left")
        ctk.CTkLabel(th_head, text="CONNECTION HEALTH", font=("Space Grotesk", 10, "bold"), text_color=GREEN).pack(side="left")
        
        self._health_box(card, 1, 0, "CURRENT PING", "14", "MS", 1.0, GREEN)
        self._health_box(card, 1, 1, "PACKET LOSS", "0.02", "%", 0.05, RED)
        self._health_box(card, 1, 2, "NETWORK JITTER", "2.4", "MS", 0.4, GREEN)

    def _health_box(self, parent, row, col, title, val, unit, fill_ratio, color):
        f = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=4)
        f.grid(row=row, column=col, padx=(0 if col==0 else 8, 0 if col==2 else 8), sticky="nsew")
        
        inner = ctk.CTkFrame(f, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(inner, text=title, font=("Space Grotesk", 9), text_color=TEXT_DIM).pack(anchor="w")
        val_f = ctk.CTkFrame(inner, fg_color="transparent")
        val_f.pack(anchor="w", pady=(8, 20))
        ctk.CTkLabel(val_f, text=val, font=("Space Grotesk", 32, "bold"), text_color=TEXT).pack(side="left")
        ctk.CTkLabel(val_f, text=" "+unit, font=("Space Grotesk", 12, "bold"), text_color=color).pack(side="left", pady=(10, 0))
        
        bar = ctk.CTkFrame(inner, fg_color=BG_INPUT, height=4, corner_radius=2)
        bar.pack(fill="x", anchor="w")
        fill_w = max(1, int(150 * fill_ratio))
        ctk.CTkFrame(bar, fg_color=color, height=4, width=fill_w, corner_radius=2).place(x=0, y=0)

    def _build_ports(self, parent, row, col):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=4)
        card.grid(row=row, column=col, padx=(0, 12), pady=(0, 16), sticky="nsew")
        
        th_head = ctk.CTkFrame(card, fg_color="transparent")
        th_head.pack(fill="x", padx=16, pady=20)
        ctk.CTkLabel(th_head, text="ACTIVE PORTS & PROTOCOLS", font=("Space Grotesk", 10, "bold"), text_color=GREEN).pack(side="left")
        
        box = ctk.CTkFrame(card, fg_color="transparent")
        box.pack(fill="both", expand=True, padx=16, pady=(0, 16))
        
        self._port_row(box, "TCP", "RTSP STREAM", "554", active=True)
        self._port_row(box, "UDP", "P2P SIGNALING", "12440", active=True)
        self._port_row(box, "TCP", "WEB UI (HTTPS)", "443", active=True)
        self._port_row(box, "FTP", "UPDATE SERVICE", "21", active=False)

    def _port_row(self, parent, proto, name, port, active=True):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=6)
        
        bg = "#12251a" if active else BG_CARD_L
        tc = GREEN if active else TEXT_DIM
        nc = TEXT if active else TEXT_DIM
        pc = TEXT if active else GRAY
        
        badge = ctk.CTkFrame(row, fg_color=bg, border_color=bg, border_width=1, corner_radius=4)
        badge.pack(side="left")
        ctk.CTkLabel(badge, text=proto, font=("Courier New", 9, "bold"), text_color=tc).pack(padx=6, pady=2)
        
        ctk.CTkLabel(row, text="  " + name, font=("Space Grotesk", 11), text_color=nc).pack(side="left")
        
        pF = ctk.CTkFrame(row, fg_color="transparent")
        pF.pack(side="right")
        ctk.CTkLabel(pF, text="PORT ", font=("Space Grotesk", 9), text_color=TEXT_DIM).pack(side="left")
        ctk.CTkLabel(pF, text=port, font=("Courier New", 11, "bold"), text_color=pc).pack(side="left")

    def _build_device_discovery(self, parent, row, col):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=4)
        card.grid(row=row, column=col, columnspan=2, padx=(12, 0), pady=(0, 16), sticky="nsew")
        card.grid_columnconfigure((0,1,2,3), weight=1)
        
        th_head = ctk.CTkFrame(card, fg_color="transparent")
        th_head.grid(row=0, column=0, columnspan=4, sticky="ew", padx=16, pady=20)
        ctk.CTkLabel(th_head, text="\uE73E", font=("Segoe MDL2 Assets", 12), text_color=GREEN).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(th_head, text="DEVICE DISCOVERY", font=("Space Grotesk", 10, "bold"), text_color=GREEN).pack(side="left")
        
        nodesbg = ctk.CTkFrame(th_head, fg_color=BG_CARD_L, corner_radius=4)
        nodesbg.pack(side="right")
        ctk.CTkLabel(nodesbg, text=" 12 NODES ONLINE ", font=("Space Grotesk", 9, "bold"), text_color=TEXT_DIM).pack(padx=6, pady=2)
        
        hY = 1
        for i, h in enumerate(["DEVICE IDENTITY", "NETWORK ROLE", "CONNECTION", "THROUGHPUT"]):
            ctk.CTkLabel(card, text=h, font=("Space Grotesk", 9), text_color=TEXT_DIM).grid(row=hY, column=i, sticky="w" if i<3 else "e", padx=20, pady=(0, 12))
            
        self._dev_row(card, 2, "CAM-LOBBY-01", "192.168.1.105", "PRIMARY OPTIC", "\uE701", "WPA3_CORP", "4.2 MB/s", GREEN)
        self._dev_row(card, 3, "NAS-BACKUP-SVR", "192.168.1.12", "STORAGE HUB", "\uE81E", "1Gbps Link", "12.8 MB/s", GREEN)
        self._dev_row(card, 4, "SYS_ADMIN_PAD", "192.168.1.55", "TERMINAL", "\uE701", "Guest_Ext", "0.1 MB/s", TEXT_DIM)

    def _dev_row(self, parent, row, name, ip, role, conn_icon, conn_text, tp_text, style_col):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=0, columnspan=4, sticky="ew", padx=20, pady=10)
        f.grid_columnconfigure((0,1,2,3), weight=1)
        
        c1 = ctk.CTkFrame(f, fg_color="transparent")
        c1.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(c1, text=name, font=("Space Grotesk", 11, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(c1, text=ip, font=("Courier New", 9), text_color=TEXT_DIM).pack(anchor="w")
        
        c2 = ctk.CTkFrame(f, fg_color="transparent")
        c2.grid(row=0, column=1, sticky="w")
        bg_c = "#12251a" if style_col==GREEN else "transparent"
        border_c = GREEN if style_col==GREEN else GRAY
        r_f = ctk.CTkFrame(c2, fg_color=bg_c, border_width=1, border_color=border_c, corner_radius=2)
        r_f.pack(anchor="w")
        ctk.CTkLabel(r_f, text=role, font=("Space Grotesk", 8, "bold"), text_color=style_col).pack(padx=6, pady=2)
        
        c3 = ctk.CTkFrame(f, fg_color="transparent")
        c3.grid(row=0, column=2, sticky="w")
        ctk.CTkLabel(c3, text=conn_icon, font=("Segoe MDL2 Assets", 12), text_color=style_col).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(c3, text=conn_text, font=("Space Grotesk", 10), text_color=TEXT).pack(side="left")
        
        c4 = ctk.CTkFrame(f, fg_color="transparent")
        c4.grid(row=0, column=3, sticky="e")
        ctk.CTkLabel(c4, text=tp_text, font=("Courier New", 10, "bold"), text_color=TEXT).pack(anchor="e")

    def _build_adv_routing(self, parent, row):
        card = ctk.CTkFrame(parent, fg_color="transparent", border_width=1, border_color=GRAY_DARK, corner_radius=4)
        card.grid(row=row, column=0, columnspan=3, pady=(0, 16), sticky="nsew")
        
        ctk.CTkFrame(card, width=4, corner_radius=0, fg_color=GREEN).pack(side="left", fill="y")
        
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=24)
        
        shield_frame = ctk.CTkFrame(inner, fg_color=BG_CARD_L, corner_radius=12, width=48, height=48, border_width=1, border_color=GREEN)
        shield_frame.pack_propagate(False)
        shield_frame.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(shield_frame, text="\uE773", font=("Segoe MDL2 Assets", 20), text_color=GREEN).place(relx=0.5, rely=0.5, anchor="center")
        
        desc_f = ctk.CTkFrame(inner, fg_color="transparent")
        desc_f.pack(side="left", padx=(0, 40))
        ctk.CTkLabel(desc_f, text="ADVANCED ROUTING ENGINE", font=("Space Grotesk", 12, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(desc_f, text="Real-time analysis of NAT traversal and relay\ninfrastructure for secure P2P encryption.", font=("Space Grotesk", 10), text_color=TEXT_DIM, justify="left").pack(anchor="w", pady=(4, 0))
        
        boxes = ctk.CTkFrame(inner, fg_color="transparent")
        boxes.pack(side="right", fill="y", anchor="e")
        
        boxes.grid_rowconfigure((0, 1), weight=1)
        
        self._adv_box(boxes, 0, 0, "NAT TYPE", "CONE (TYPE 2)", GREEN)
        self._adv_box(boxes, 0, 1, "STUN STATUS", "\u25CF REACHABLE", TEXT)
        self._adv_box(boxes, 0, 2, "TURN RELAY", "\u25CF INACTIVE", TEXT_DIM)
        
        self._adv_box(boxes, 1, 0, "ENCRYPTION", "AES-256-GCM", TEXT)

    def _adv_box(self, parent, r, c, lbl, val, color):
        f = ctk.CTkFrame(parent, fg_color=BG_CARD_L, corner_radius=4, width=140, height=60)
        f.grid_propagate(False)
        f.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
        f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(f, text=lbl, font=("Space Grotesk", 8), text_color=TEXT_DIM).grid(row=0, column=0, sticky="w", padx=16, pady=(12, 0))
        ctk.CTkLabel(f, text=val, font=("Space Grotesk", 11, "bold"), text_color=color).grid(row=1, column=0, sticky="w", padx=16, pady=(4, 12))
