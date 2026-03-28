import customtkinter as ctk
import socket
import threading
import subprocess
import os

BG_PANEL   = "#0e0e0e"
BG_CARD    = "#171717"
BG_CARD_L  = "#1f1f1f"
BG_INPUT   = "#141414"
BG_BADGE   = "#0d1a13"
GREEN      = "#3fff8b"
GREEN_TXT  = "#005d2c"
GREEN_DIM  = "#24f07e"
TEXT       = "#ffffff"
TEXT_DIM   = "#8a8a8a"
GRAY       = "#333333"
GRAY_MED   = "#555555"
RED        = "#ff716c"
YELLOW     = "#f39c12"


class NetworkInfoFrame(ctk.CTkFrame):
    def __init__(self, master, app_ref, *args, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, corner_radius=0, *args, **kwargs)
        self.app_ref = app_ref
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._labels = {}

        self._build_header()
        self._build_content()

        threading.Thread(target=self._scan_all, daemon=True).start()

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self):
        h = ctk.CTkFrame(self, fg_color="transparent")
        h.grid(row=0, column=0, padx=28, pady=(22, 0), sticky="ew")
        h.grid_columnconfigure(1, weight=1)

        # Title block
        titles = ctk.CTkFrame(h, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(titles, text="NETWORK TOPOLOGY",
                     font=("Space Grotesk", 28, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(titles, text="TELEMETRY ENGINE // LIVE DATA FEED",
                     font=("Space Grotesk", 10, "bold"), text_color=TEXT_DIM).pack(anchor="w", pady=(2, 0))

        # Buttons
        btns = ctk.CTkFrame(h, fg_color="transparent")
        btns.grid(row=0, column=2, sticky="e")

        ctk.CTkButton(btns, text="\uE72C  RE-SCAN NETWORK",
                      font=("Space Grotesk", 10, "bold"), height=34,
                      fg_color="transparent", border_width=1, border_color=GRAY,
                      text_color=GREEN, hover_color=BG_CARD_L,
                      command=self._rescan).pack(side="left", padx=(0, 10))

        ctk.CTkButton(btns, text="\uE896  EXPORT LOGS",
                      font=("Space Grotesk", 10, "bold"), height=34,
                      fg_color=GREEN, text_color=GREEN_TXT, hover_color=GREEN_DIM,
                      command=self._export_logs).pack(side="left")

    # ── Main Content ──────────────────────────────────────────────────────────
    def _build_content(self):
        wrap = ctk.CTkFrame(self, fg_color="transparent")
        wrap.grid(row=1, column=0, padx=28, pady=20, sticky="nsew")
        wrap.grid_columnconfigure(0, weight=1)
        wrap.grid_rowconfigure(2, weight=1)

        # ── Row 1: Basic Config + Connection Health ──
        row1 = ctk.CTkFrame(wrap, fg_color="transparent")
        row1.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        row1.grid_columnconfigure(0, minsize=260, weight=0)
        row1.grid_columnconfigure(1, weight=1)

        self._build_basic_config(row1)
        self._build_conn_health(row1)

        # ── Row 2: Ports + Device Discovery ──
        row2 = ctk.CTkFrame(wrap, fg_color="transparent")
        row2.grid(row=1, column=0, sticky="ew", pady=(0, 14))
        row2.grid_columnconfigure(0, weight=1)
        row2.grid_columnconfigure(1, weight=2)

        self._build_ports(row2)
        self._build_device_discovery(row2)

        # ── Row 3: Advanced Routing (full width) ──
        self._build_adv_routing(wrap)

    # ── Basic Configuration ────────────────────────────────────────────────────
    def _build_basic_config(self, parent):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=6)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(20, 16))
        dot = ctk.CTkLabel(hdr, text="\u25CF ", font=("Segoe UI", 11), text_color=GREEN)
        dot.pack(side="left")
        ctk.CTkLabel(hdr, text="BASIC CONFIGURATION",
                     font=("Space Grotesk", 9, "bold"), text_color=GREEN).pack(side="left")
        ctk.CTkLabel(hdr, text="\uE946", font=("Segoe MDL2 Assets", 16), text_color=GRAY).pack(side="right")

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        self._labels["local_ip"]   = self._cfg_row(body, "LOCAL IP ADDRESS",  "scanning...", highlight=True)
        self._labels["public_ip"]  = self._cfg_row(body, "PUBLIC IP ADDRESS",  "scanning...")
        self._labels["hostname"]   = self._cfg_row(body, "HOSTNAME",           "scanning...")
        self._labels["mac"]        = self._cfg_row(body, "MAC ADDRESS",        "—")

    def _cfg_row(self, parent, key, val, highlight=False):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", pady=5)
        ctk.CTkLabel(row, text=key, font=("Space Grotesk", 9), text_color=TEXT_DIM).pack(side="left")
        if highlight:
            pill = ctk.CTkFrame(row, fg_color=BG_BADGE, corner_radius=4,
                                border_width=1, border_color="#1a4028")
            pill.pack(side="right")
            lbl = ctk.CTkLabel(pill, text=val, font=("Courier New", 11, "bold"), text_color=GREEN)
            lbl.pack(padx=8, pady=2)
        else:
            lbl = ctk.CTkLabel(row, text=val, font=("Courier New", 11, "bold"), text_color=TEXT)
            lbl.pack(side="right")
        return lbl

    # ── Connection Health ──────────────────────────────────────────────────────
    def _build_conn_health(self, parent):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=6)
        card.grid(row=0, column=1, sticky="nsew")
        card.grid_columnconfigure((0, 1, 2), weight=1)
        card.grid_rowconfigure(1, weight=1)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=(20, 16))
        ctk.CTkLabel(hdr, text="\u25CF ", font=("Segoe UI", 11), text_color=GREEN).pack(side="left")
        ctk.CTkLabel(hdr, text="CONNECTION HEALTH",
                     font=("Space Grotesk", 9, "bold"), text_color=GREEN).pack(side="left")

        self._lat_lbl, self._lat_bar   = self._metric_box(card, 0, "CURRENT PING",   "—",  "MS",  GREEN)
        self._loss_lbl, self._loss_bar = self._metric_box(card, 1, "PACKET LOSS",     "—",  "%",   RED)
        self._jit_lbl, self._jit_bar   = self._metric_box(card, 2, "NETWORK JITTER",  "—",  "MS",  GREEN)

    def _metric_box(self, parent, col, title, val, unit, color):
        pad = (0, 1) if col == 0 else ((1, 1) if col == 1 else (1, 0))
        cell = ctk.CTkFrame(parent, fg_color=BG_CARD_L, corner_radius=0)
        cell.grid(row=1, column=col, padx=pad, pady=(0, 20), sticky="nsew")
        inner = ctk.CTkFrame(cell, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=20)
        ctk.CTkLabel(inner, text=title, font=("Space Grotesk", 9), text_color=TEXT_DIM).pack(anchor="w")
        row = ctk.CTkFrame(inner, fg_color="transparent")
        row.pack(anchor="w", pady=(10, 16))
        v_lbl = ctk.CTkLabel(row, text=val, font=("Space Grotesk", 36, "bold"), text_color=TEXT)
        v_lbl.pack(side="left")
        ctk.CTkLabel(row, text=f"  {unit}",
                     font=("Space Grotesk", 12, "bold"), text_color=color).pack(side="left", pady=(12, 0))
        bar_bg = ctk.CTkFrame(inner, fg_color=BG_INPUT, height=3, corner_radius=2)
        bar_bg.pack(fill="x")
        fill = ctk.CTkFrame(bar_bg, fg_color=color, height=3, corner_radius=2)
        fill.place(x=0, y=0, relwidth=0.0)
        return v_lbl, fill

    # ── Active Ports ───────────────────────────────────────────────────────────
    def _build_ports(self, parent):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=6)
        card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=20, pady=(20, 12))
        ctk.CTkLabel(hdr, text="ACTIVE PORTS & PROTOCOLS",
                     font=("Space Grotesk", 9, "bold"), text_color=GREEN).pack(side="left")

        body = ctk.CTkFrame(card, fg_color="transparent")
        body.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self._port_row(body, "TCP", "RTSP STREAM",   "554",   GREEN,   True)
        self._port_row(body, "UDP", "P2P SIGNALING", "12440", GREEN,   True)
        self._port_row(body, "TCP", "WEB UI (HTTPS)", "443",  GREEN,   False)
        self._port_row(body, "FTP", "UPDATE SERVICE", "21",   TEXT_DIM, False)

    def _port_row(self, parent, proto, name, port, color, active):
        row = ctk.CTkFrame(parent, fg_color="transparent", height=32)
        row.pack(fill="x", pady=3)
        row.pack_propagate(False)
        proto_bg = BG_BADGE if active else BG_CARD_L
        badge = ctk.CTkFrame(row, fg_color=proto_bg, corner_radius=3, width=38, height=22)
        badge.pack_propagate(False)
        badge.pack(side="left", padx=(0, 10), pady=5)
        ctk.CTkLabel(badge, text=proto, font=("Courier New", 8, "bold"), text_color=color).place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(row, text=name, font=("Space Grotesk", 10), text_color=TEXT if active else TEXT_DIM).pack(side="left", pady=5)
        ctk.CTkLabel(row, text=f"PORT  {port}", font=("Courier New", 10, "bold"),
                     text_color=TEXT if active else GRAY_MED).pack(side="right", pady=5, padx=4)

    # ── Device Discovery ───────────────────────────────────────────────────────
    def _build_device_discovery(self, parent):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=6)
        card.grid(row=0, column=1, sticky="nsew")
        card.grid_columnconfigure((0, 1, 2, 3), weight=1)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.grid(row=0, column=0, columnspan=4, sticky="ew", padx=20, pady=(20, 4))
        ctk.CTkLabel(hdr, text="\uE73E", font=("Segoe MDL2 Assets", 11), text_color=GREEN).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(hdr, text="DEVICE DISCOVERY", font=("Space Grotesk", 9, "bold"), text_color=GREEN).pack(side="left")
        badge = ctk.CTkFrame(hdr, fg_color=BG_CARD_L, corner_radius=4)
        badge.pack(side="right")
        ctk.CTkLabel(badge, text=" 12 NODES ONLINE ", font=("Space Grotesk", 8, "bold"), text_color=TEXT_DIM).pack(padx=4, pady=2)

        for i, h in enumerate(["DEVICE IDENTITY", "NETWORK ROLE", "CONNECTION", "THROUGHPUT"]):
            ctk.CTkLabel(card, text=h, font=("Space Grotesk", 8), text_color=TEXT_DIM).grid(
                row=1, column=i, sticky="w" if i < 3 else "e", padx=20, pady=(4, 8))

        self._dev_row(card, 2, "CAM-LOBBY-01",  "192.168.1.105", "PRIMARY OPTIC",  "\uE701", "WPA3_CORP",  "4.2 MB/s",  GREEN)
        self._dev_row(card, 3, "NAS-BACKUP-SVR", "192.168.1.12", "STORAGE HUB",    "\uE81E", "1Gbps Link", "12.8 MB/s", GREEN)
        self._dev_row(card, 4, "SYS_ADMIN_PAD",  "192.168.1.55", "TERMINAL",       "\uE701", "Guest_Ext",  "0.1 MB/s",  TEXT_DIM)

    def _dev_row(self, parent, row, name, ip, role, icon, conn, tp, style):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=row, column=0, columnspan=4, sticky="ew", padx=20, pady=8)
        f.grid_columnconfigure((0, 1, 2, 3), weight=1)

        c1 = ctk.CTkFrame(f, fg_color="transparent")
        c1.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(c1, text=name, font=("Space Grotesk", 11, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(c1, text=ip,   font=("Courier New", 9), text_color=TEXT_DIM).pack(anchor="w")

        c2 = ctk.CTkFrame(f, fg_color="transparent")
        c2.grid(row=0, column=1, sticky="w")
        role_bg = BG_BADGE if style == GREEN else "transparent"
        r_f = ctk.CTkFrame(c2, fg_color=role_bg, border_width=1,
                            border_color=GREEN if style == GREEN else GRAY, corner_radius=3)
        r_f.pack(anchor="w")
        ctk.CTkLabel(r_f, text=role, font=("Space Grotesk", 8, "bold"), text_color=style).pack(padx=6, pady=2)

        c3 = ctk.CTkFrame(f, fg_color="transparent")
        c3.grid(row=0, column=2, sticky="w")
        ctk.CTkLabel(c3, text=icon, font=("Segoe MDL2 Assets", 12), text_color=style).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(c3, text=conn, font=("Space Grotesk", 10), text_color=TEXT).pack(side="left")

        ctk.CTkLabel(f, text=tp, font=("Courier New", 10, "bold"),
                     text_color=TEXT).grid(row=0, column=3, sticky="e")

    # ── Advanced Routing ───────────────────────────────────────────────────────
    def _build_adv_routing(self, parent):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=6,
                            border_width=1, border_color=GRAY)
        card.grid(row=2, column=0, sticky="nsew", pady=(0, 8))
        card.grid_columnconfigure(1, weight=1)

        accent = ctk.CTkFrame(card, width=4, corner_radius=0, fg_color=GREEN)
        accent.pack(side="left", fill="y")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="both", expand=True, padx=24, pady=22, side="left")

        shield = ctk.CTkFrame(inner, fg_color=BG_CARD_L, corner_radius=12, width=44, height=44,
                              border_width=1, border_color=GREEN)
        shield.pack_propagate(False)
        shield.pack(side="left", padx=(0, 20))
        ctk.CTkLabel(shield, text="\uE773", font=("Segoe MDL2 Assets", 18), text_color=GREEN
                     ).place(relx=0.5, rely=0.5, anchor="center")

        desc = ctk.CTkFrame(inner, fg_color="transparent")
        desc.pack(side="left", padx=(0, 40))
        ctk.CTkLabel(desc, text="ADVANCED ROUTING ENGINE",
                     font=("Space Grotesk", 12, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(desc, text="Real-time analysis of NAT traversal and relay\ninfrastructure for secure P2P encryption.",
                     font=("Space Grotesk", 10), text_color=TEXT_DIM, justify="left").pack(anchor="w", pady=(4, 0))

        grid_f = ctk.CTkFrame(card, fg_color="transparent")
        grid_f.pack(side="right", padx=24, pady=22, fill="y", anchor="e")
        grid_f.grid_rowconfigure((0, 1), weight=1)

        self._adv_box(grid_f, 0, 0, "NAT TYPE",    "CONE (TYPE 2)", GREEN)
        self._adv_box(grid_f, 0, 1, "STUN STATUS", "\u25CF REACHABLE", TEXT)
        self._adv_box(grid_f, 0, 2, "TURN RELAY",  "\u25CF INACTIVE",  TEXT_DIM)
        self._adv_box(grid_f, 1, 0, "ENCRYPTION",  "AES-256-GCM",  TEXT)

    def _adv_box(self, parent, r, c, label, val, color):
        f = ctk.CTkFrame(parent, fg_color=BG_CARD_L, corner_radius=4, width=140, height=58)
        f.grid_propagate(False)
        f.grid(row=r, column=c, padx=4, pady=4, sticky="nsew")
        f.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(f, text=label, font=("Space Grotesk", 8), text_color=TEXT_DIM
                     ).grid(row=0, column=0, sticky="w", padx=14, pady=(10, 0))
        ctk.CTkLabel(f, text=val,   font=("Space Grotesk", 11, "bold"), text_color=color
                     ).grid(row=1, column=0, sticky="w", padx=14, pady=(2, 10))

    # ── Live scan ──────────────────────────────────────────────────────────────
    def _scan_all(self):
        local_ip  = self._get_local_ip()
        hostname  = socket.gethostname()
        public_ip = self._get_public_ip()
        lat, loss = self._ping("8.8.8.8")

        def update():
            try:
                self._labels["local_ip"].configure(text=local_ip)
                self._labels["public_ip"].configure(text=public_ip)
                self._labels["hostname"].configure(text=hostname)

                if lat:
                    self._lat_lbl.configure(text=str(lat))
                    self._lat_bar.place(relwidth=min(1.0, lat / 200.0))
                self._loss_lbl.configure(text=str(loss))
                self._loss_bar.place(relwidth=min(1.0, loss / 100.0))
                self._jit_lbl.configure(text="<5")
                self._jit_bar.place(relwidth=0.05)
            except Exception:
                pass

        self.after(0, update)

    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("10.255.255.255", 1))
            return s.getsockname()[0]
        except:
            return "127.0.0.1"
        finally:
            try: s.close()
            except: pass

    def _get_public_ip(self):
        try:
            import urllib.request
            return urllib.request.urlopen("https://api.ipify.org", timeout=4).read().decode()
        except:
            return "Unavailable"

    def _ping(self, host):
        try:
            r = subprocess.run(["ping", "-n", "4", host], capture_output=True, text=True, timeout=8)
            lat = loss = 0
            for line in r.stdout.splitlines():
                if "Average" in line or "Minimum" in line:
                    p = line.split("=")
                    if p:
                        try: lat = int(p[-1].strip().replace("ms", "").strip())
                        except: pass
                if "Lost" in line or "loss" in line.lower():
                    for part in line.split(","):
                        if "%" in part:
                            try: loss = int(part.strip().split()[0].replace("%", "").replace("(", ""))
                            except: pass
            return lat, loss
        except:
            return None, 0

    def _rescan(self):
        for k in self._labels:
            self._labels[k].configure(text="scanning...")
        self._lat_lbl.configure(text="—")
        self._loss_lbl.configure(text="—")
        self._jit_lbl.configure(text="—")
        threading.Thread(target=self._scan_all, daemon=True).start()

    def _export_logs(self):
        from tkinter import filedialog
        local  = self._labels["local_ip"].cget("text")
        public = self._labels["public_ip"].cget("text")
        host   = self._labels["hostname"].cget("text")
        lat    = self._lat_lbl.cget("text")
        loss   = self._loss_lbl.cget("text")
        content = (
            f"CamXtract \u2014 Network Info Export\n{'='*40}\n"
            f"Local IP:     {local}\nPublic IP:    {public}\n"
            f"Hostname:     {host}\nLatency:      {lat} ms\nPacket Loss:  {loss}%\n"
        )
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text Files", "*.txt")])
        if path:
            with open(path, "w") as f:
                f.write(content)
