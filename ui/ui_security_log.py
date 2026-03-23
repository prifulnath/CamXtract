import customtkinter as ctk
import os
from datetime import datetime, timezone
from tkinter import filedialog, simpledialog

BG_PANEL   = "#0e0e0e"
BG_CARD    = "#1a1919"
BG_CARD_H  = "#262626"
BG_CARD_L  = "#131313"
BG_ALERT   = "#1c0a0c"
BG_GLASS   = "#1d1d1d"
GREEN      = "#3fff8b"
GREEN_TXT  = "#005d2c"
GREEN_DIM  = "#24f07e"
CYAN       = "#45fec9"
CYAN_DIM   = "#2cefbc"
TEXT       = "#ffffff"
TEXT_DIM   = "#adaaaa"
GRAY       = "#494847"
GRAY_DARK  = "#333333"
RED        = "#ff716c"
RED_DIM    = "#d7383b"
ERR_BG     = "#1c0a0c"


class SecurityLogFrame(ctk.CTkFrame):
    def __init__(self, master, app_ref, *args, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, corner_radius=0, *args, **kwargs)
        self.app_ref = app_ref

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_header()

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, padx=24, pady=16, sticky="nsew")
        content.grid_columnconfigure(0, weight=0, minsize=280)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        self._build_left_col(content)
        self._build_right_col(content)

        self._build_footer()

    # ── Header ────────────────────────────────────────────────────────────────
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
        ctk.CTkLabel(titles, text="REAL-TIME THREAT MONITORING AND ACCESS PROTOCOLS",
                     font=("Space Grotesk", 10, "bold"), text_color=TEXT_DIM).pack(anchor="w")

        btns = ctk.CTkFrame(header, fg_color="transparent")
        btns.grid(row=0, column=1, sticky="e")

        ctk.CTkButton(btns, text="\uE72C  REFRESH",
                      font=("Space Grotesk", 10, "bold"), height=34,
                      fg_color=BG_CARD_H, border_width=1, border_color=GRAY,
                      text_color=TEXT, hover_color="#303030",
                      command=self._refresh).pack(side="left", padx=(0, 10))

        ctk.CTkButton(btns, text="\uE896  DOWNLOAD LOGS",
                      font=("Space Grotesk", 10, "bold"), height=34,
                      fg_color=GREEN, text_color=GREEN_TXT, hover_color=GREEN_DIM,
                      command=self._download_logs).pack(side="left")

    # ── Left Column ────────────────────────────────────────────────────────────
    def _build_left_col(self, parent):
        left = ctk.CTkScrollableFrame(parent, fg_color="transparent", scrollbar_button_color=BG_CARD_H)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 12))

        # Section label
        th = ctk.CTkFrame(left, fg_color="transparent")
        th.pack(fill="x", pady=(4, 12))
        ctk.CTkLabel(th, text="\u25CF ", font=("Segoe UI", 11), text_color=GREEN).pack(side="left")
        ctk.CTkLabel(th, text="ACTIVE THREATS", font=("Space Grotesk", 9, "bold"), text_color=GREEN).pack(side="left")

        # Alert cards — compact horizontal layout
        self._alert_card(left,
            is_crit=True, icon="\uE730", icon_col=RED,
            title="UNAUTHORIZED ACCESS ATTEMPT",
            detail="IP: 192.168.1.104",
            meta="DETECTED: 2M AGO \u2022 LOCATION: BEIJING, CN")

        self._alert_card(left,
            is_crit=False, icon="\uE916", icon_col=GREEN_DIM,
            title="BRUTE FORCE WARNING",
            detail="Multiple failed logins (Admin)",
            meta="DETECTED: 14M AGO \u2022 ORIGIN: VPN NODE #14")

        self._alert_card(left,
            is_crit=False, icon="\uE9A2", icon_col=CYAN_DIM,
            title="SUSPICIOUS IP PATTERN",
            detail="IP: 45.2.118.9",
            meta="DETECTED: 1H AGO \u2022 STATUS: MONITORED")

        self._ssl_card(left)

    def _alert_card(self, parent, is_crit, icon, icon_col, title, detail, meta):
        bg = ERR_BG if is_crit else BG_CARD
        border = RED_DIM if is_crit else GRAY_DARK
        card = ctk.CTkFrame(parent, fg_color=bg, corner_radius=6,
                            border_width=1, border_color=border)
        card.pack(fill="x", pady=(0, 10))

        # Left accent bar for critical
        if is_crit:
            accent = ctk.CTkFrame(card, width=3, corner_radius=0, fg_color=RED)
            accent.pack(side="left", fill="y")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", expand=False, padx=10, pady=5)

        # Top row: icon + title
        top = ctk.CTkFrame(inner, fg_color="transparent")
        top.pack(fill="x")
        ctk.CTkLabel(top, text=icon, font=("Segoe MDL2 Assets", 14), text_color=icon_col).pack(side="left", padx=(0, 8))
        ctk.CTkLabel(top, text=title, font=("Space Grotesk", 10, "bold"),
                     text_color=RED if is_crit else TEXT).pack(side="left", anchor="w")

        # Detail — indented to align with title (past icon)
        ctk.CTkLabel(inner, text=detail,
                     font=("Courier New", 12, "bold") if "IP:" in detail else ("Space Grotesk", 11),
                     text_color=TEXT, anchor="w").pack(anchor="w", padx=(26, 0), pady=(2, 0))

        # Meta — same indent
        ctk.CTkLabel(inner, text=meta, font=("Space Grotesk", 8, "bold"),
                     text_color=TEXT_DIM, anchor="w").pack(anchor="w", padx=(26, 0), pady=(2, 0))

    def _ssl_card(self, parent):
        card = ctk.CTkFrame(parent, fg_color=BG_GLASS, corner_radius=8,
                            border_width=1, border_color=GRAY_DARK)
        card.pack(fill="x", pady=(6, 0))
        card.grid_columnconfigure(1, weight=1)

        # Header
        head = ctk.CTkFrame(card, fg_color="transparent")
        head.grid(row=0, column=0, columnspan=2, sticky="ew", padx=14, pady=(14, 8))
        ctk.CTkLabel(head, text="SSL CERTIFICATE", font=("Space Grotesk", 9, "bold"), text_color=TEXT).pack(side="left")

        # Read real cert
        expiry_str, issuer_str, days_left, is_valid = self._read_cert()
        badge_bg = "#12251a" if is_valid else "#250c0e"
        badge_txt = "ACTIVE" if is_valid else ("EXPIRED" if days_left < 0 else "MISSING")
        badge_col = GREEN if is_valid else RED
        badge = ctk.CTkFrame(head, fg_color=badge_bg, corner_radius=8)
        badge.pack(side="right")
        ctk.CTkLabel(badge, text=badge_txt, font=("Space Grotesk", 8, "bold"), text_color=badge_col).pack(padx=8, pady=2)

        self._ssl_row(card, 1, "ISSUER",   issuer_str)
        self._ssl_row(card, 2, "PROTOCOL", "TLS 1.3")
        exp_col = GREEN if days_left > 30 else (RED if days_left < 7 else "#f39c12")
        self._ssl_row(card, 3, "EXPIRY",   expiry_str, exp_col)

        progress = max(0.0, min(1.0, days_left / 365)) if is_valid else 0.0
        bar_bg = ctk.CTkFrame(card, fg_color=BG_CARD_H, height=5, corner_radius=3)
        bar_bg.grid(row=4, column=0, columnspan=2, sticky="ew", padx=14, pady=(10, 16))
        bar_bg.grid_propagate(False)
        bar_col = GREEN if progress > 0.3 else ("#f39c12" if progress > 0.1 else RED)
        ctk.CTkFrame(bar_bg, fg_color=bar_col, height=5, corner_radius=3).place(relwidth=progress, rely=0)

    def _ssl_row(self, parent, r, k, v, color=None):
        ctk.CTkLabel(parent, text=k, font=("Space Grotesk", 8), text_color=TEXT_DIM
                     ).grid(row=r, column=0, sticky="w", padx=14, pady=3)
        ctk.CTkLabel(parent, text=v, font=("Courier New", 10, "bold"), text_color=color or TEXT
                     ).grid(row=r, column=1, sticky="e", padx=14, pady=3)

    def _read_cert(self):
        cert_path = "cert.pem"
        if not os.path.exists(cert_path):
            return "Not found", "N/A", 0, False
        try:
            from cryptography import x509
            with open(cert_path, "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())
            exp = cert.not_valid_after_utc
            now = datetime.now(timezone.utc)
            days = (exp - now).days
            issuer = cert.issuer.get_attributes_for_oid(x509.NameOID.COMMON_NAME)
            issuer_str = issuer[0].value if issuer else "Self-Signed"
            expiry_str = f"{exp.strftime('%Y-%m-%d')}  ({days}d)"
            return expiry_str, issuer_str, days, days > 0
        except Exception as e:
            return f"Error: {e}", "N/A", 0, False

    # ── Right Column ───────────────────────────────────────────────────────────
    def _build_right_col(self, parent):
        right = ctk.CTkFrame(parent, fg_color=BG_CARD_L, corner_radius=8,
                             border_width=1, border_color=GRAY_DARK)
        right.grid(row=0, column=1, sticky="nsew")
        right.grid_columnconfigure(0, weight=1)
        right.grid_rowconfigure(1, weight=1)

        # Tab bar
        tabs_wrap = ctk.CTkFrame(right, fg_color="transparent")
        tabs_wrap.grid(row=0, column=0, sticky="ew", padx=16, pady=(14, 0))

        tabs_row = ctk.CTkFrame(tabs_wrap, fg_color="transparent")
        tabs_row.pack(fill="x")

        active_lbl = ctk.CTkLabel(tabs_row, text="ALL ACTIVITY",
                                  font=("Space Grotesk", 10, "bold"), text_color=GREEN)
        active_lbl.pack(side="left", padx=(0, 20))
        ctk.CTkFrame(tabs_wrap, fg_color=GREEN, height=2).pack(anchor="w", pady=(2, 0))
        ctk.CTkFrame(tabs_wrap, fg_color=GREEN, height=2, width=90).place(x=0, y=22)

        for tab in ["FAILURES", "SSH"]:
            ctk.CTkLabel(tabs_row, text=tab, font=("Space Grotesk", 10, "bold"),
                         text_color=TEXT_DIM).pack(side="left", padx=16)

        live = ctk.CTkFrame(tabs_row, fg_color="transparent")
        live.pack(side="right")
        ctk.CTkLabel(live, text="\u25CF ", font=("Segoe UI", 8), text_color=GREEN).pack(side="left")
        ctk.CTkLabel(live, text="LIVE_STREAM_ENABLED", font=("Courier New", 8, "bold"),
                     text_color=TEXT_DIM).pack(side="left")

        sep = ctk.CTkFrame(right, fg_color=GRAY_DARK, height=1)
        sep.grid(row=0, column=0, sticky="ew", pady=(46, 0))

        # Log list (scrollable rows)
        self.log_scroll = ctk.CTkScrollableFrame(right, fg_color="transparent",
                                                  scrollbar_button_color=BG_CARD_H)
        self.log_scroll.grid(row=1, column=0, sticky="nsew", padx=8, pady=8)
        self.log_scroll.grid_columnconfigure(0, weight=1)
        self._populate_logs()

        # Separator
        ctk.CTkFrame(right, fg_color=GRAY_DARK, height=1).grid(row=2, column=0, sticky="ew")

        # Action buttons
        actions = ctk.CTkFrame(right, fg_color="transparent")
        actions.grid(row=3, column=0, sticky="ew", padx=12, pady=12)
        actions.grid_columnconfigure((0, 1, 2, 3), weight=1)

        self._action_btn(actions, 0, RED,      "\uE735", "BLOCK IP",   command=self._block_ip)
        self._action_btn(actions, 1, GREEN,    "\uE73A", "ALLOWLIST")
        self._action_btn(actions, 2, CYAN,     "\uE756", "CLI ACCESS")
        self._action_btn(actions, 3, TEXT_DIM, "\uE74D", "CLEAR LOGS", command=self._clear_logs)

    # Log row entries
    LOG_DATA = [
        ("[14:22:01]", "AUTH_SUCCESS", GREEN,    " User ",        "ADMIN_SRV",       GREEN,    " logged in via WEB_UI",                    "172.16.0.45"),
        ("[14:21:44]", "AUTH_FAILED",  RED_DIM,  " Invalid creds for user ", "ROOT",  RED,      " (Attempt 3/5)",                           "192.168.1.104"),
        ("[14:18:32]", "SYS_CONFIG",   GREEN,    " Firewall rules updated: ", "BLOCK_LIST_SYNC", CYAN_DIM, " completed",                   "INTERNAL"),
        ("[14:15:10]", "CONN_INFO",    CYAN_DIM, " New session via SSH: ",   "terminal_agent_09", "#888888", "",                           "10.0.4.21"),
        ("[14:10:05]", "AUTH_FAILED",  RED_DIM,  " Invalid creds for user ", "ROOT",  RED,      " (Attempt 2/5)",                           "192.168.1.104"),
        ("[14:05:59]", "SSL_RENEW",    GREEN_DIM," Automated cert renewal check: ", "SUCCESS", GREEN, "",                                   "SYSTEM"),
        ("[13:58:22]", "CONN_DROP",    CYAN_DIM, " Inbound connection from ", "45.2.118.9", RED, " dropped (Geofence)",                    "GATEWAY_01"),
        ("[13:45:01]", "HEARTBEAT",    "#666666", " System status: ",        "OPTIMAL", GREEN_DIM, "",                                     "INTERNAL"),
        ("[13:30:00]", "HEARTBEAT",    "#666666", " System status: ",        "OPTIMAL", GREEN_DIM, "",                                     "INTERNAL"),
    ]

    def _populate_logs(self):
        for widget in self.log_scroll.winfo_children():
            widget.destroy()
        for ts, evt, evt_col, m1, m2, m2_col, m3, src in self.LOG_DATA:
            self._log_row(ts, evt, evt_col, m1, m2, m2_col, m3, src)

    def _log_row(self, ts, evt, evt_col, m1, m2, m2_col, m3, src):
        row = ctk.CTkFrame(self.log_scroll, fg_color="transparent")
        row.pack(fill="x", pady=4)
        row.grid_columnconfigure(2, weight=1)

        # Timestamp
        ctk.CTkLabel(row, text=ts, font=("Courier New", 10), text_color="#555555",
                     width=70, anchor="w").grid(row=0, column=0, sticky="w", padx=(4, 8))

        # Event badge
        badge = ctk.CTkFrame(row, fg_color="transparent", width=90)
        badge.grid(row=0, column=1, sticky="w", padx=(0, 10))
        ctk.CTkLabel(badge, text=evt, font=("Courier New", 10, "bold"),
                     text_color=evt_col, width=90, anchor="w").pack()

        # Message
        msg = ctk.CTkFrame(row, fg_color="transparent")
        msg.grid(row=0, column=2, sticky="ew")
        ctk.CTkLabel(msg, text=m1, font=("Space Grotesk", 10), text_color=TEXT_DIM).pack(side="left")
        ctk.CTkLabel(msg, text=m2, font=("Space Grotesk", 10, "bold"), text_color=m2_col).pack(side="left")
        if m3:
            ctk.CTkLabel(msg, text=m3, font=("Space Grotesk", 10), text_color=TEXT_DIM).pack(side="left")

        # Source (right-aligned)
        ctk.CTkLabel(row, text=src, font=("Courier New", 9), text_color="#444444",
                     anchor="e").grid(row=0, column=3, sticky="e", padx=(8, 4))

        # Thin separator
        ctk.CTkFrame(self.log_scroll, fg_color="#1f1f1f", height=1).pack(fill="x")

    def _action_btn(self, parent, col, color, icon, label, command=None):
        pad = (0 if col == 0 else 4, 0 if col == 3 else 4)
        f = ctk.CTkFrame(parent, fg_color=BG_CARD_H, corner_radius=6,
                         border_width=1, border_color=GRAY_DARK)
        f.grid(row=0, column=col, sticky="nsew", padx=pad)
        inner = ctk.CTkFrame(f, fg_color="transparent")
        inner.pack(expand=True, pady=14)
        ctk.CTkLabel(inner, text=icon, font=("Segoe MDL2 Assets", 18), text_color=color).pack()
        ctk.CTkLabel(inner, text=label, font=("Space Grotesk", 8, "bold"), text_color=TEXT_DIM).pack(pady=(4, 0))
        if command:
            for w in [f, inner] + inner.winfo_children():
                w.bind("<Button-1>", lambda e, c=command: c())

    # ── Footer ────────────────────────────────────────────────────────────────
    def _build_footer(self):
        foot = ctk.CTkFrame(self, fg_color="transparent")
        foot.grid(row=2, column=0, padx=24, pady=(0, 16), sticky="ew")
        foot.grid_columnconfigure((0, 1, 2, 3), weight=1)
        self._footer_card(foot, 0, "TOTAL INBOUND",  "12.4K", "+2%",   GREEN,    False)
        self._footer_card(foot, 1, "BLOCKED ATTACKS", "842",  "+12%",  RED,      False)
        self._footer_card(foot, 2, "FAILED LOGINS",   "29",   "STABLE",TEXT_DIM, False)
        self._footer_card(foot, 3, "SYSTEM UPTIME",   "99.98%","OPTIMAL",GREEN,  True)

    def _footer_card(self, parent, col, title, val, sub, sub_col, last):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=8,
                            border_width=1, border_color=GRAY_DARK)
        card.grid(row=0, column=col, sticky="nsew",
                  padx=(0 if col == 0 else 6, 0 if last else 6))
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(anchor="w", padx=18, pady=16)
        ctk.CTkLabel(inner, text=title, font=("Space Grotesk", 8, "bold"), text_color=TEXT_DIM).pack(anchor="w", pady=(0, 6))
        val_row = ctk.CTkFrame(inner, fg_color="transparent")
        val_row.pack(anchor="w")
        ctk.CTkLabel(val_row, text=val, font=("Space Grotesk", 22, "bold"), text_color=TEXT).pack(side="left")
        ctk.CTkLabel(val_row, text=" " + sub, font=("Space Grotesk", 10, "bold"), text_color=sub_col).pack(side="left", pady=(4, 0))

    # ── Actions ────────────────────────────────────────────────────────────────
    def _block_ip(self):
        ip = simpledialog.askstring("Block IP", "Enter IP address to block:", parent=self)
        if ip:
            ts = datetime.now().strftime("%H:%M:%S")
            self._log_row(f"[{ts}]", "BLOCK_IP", RED, " Blocked: ", ip, RED, "", "SYSTEM")

    def _clear_logs(self):
        for w in self.log_scroll.winfo_children():
            w.destroy()
        ts = datetime.now().strftime("%H:%M:%S")
        self._log_row(f"[{ts}]", "SYS_CLEAR", "#666666", " Log buffer cleared", "", TEXT_DIM, "", "SYSTEM")

    def _refresh(self):
        self._populate_logs()

    def _download_logs(self):
        lines = []
        for row in self.log_scroll.winfo_children():
            try:
                cells = [c.cget("text") for c in row.winfo_children() if hasattr(c, 'cget')]
                lines.append("  ".join(cells))
            except:
                pass
        path = filedialog.asksaveasfilename(defaultextension=".txt",
                                            filetypes=[("Text Files", "*.txt"), ("JSON", "*.json")],
                                            title="Export Security Logs")
        if path:
            with open(path, "w") as f:
                f.write(f"MCX CAM \u2014 Security Log Export\n{'='*40}\n")
                f.write("\n".join(lines))
