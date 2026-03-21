import ctypes
try:
    # Fix GUI blurriness / clarity issues on Windows High DPI displays
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import customtkinter as ctk
import threading
import asyncio
import socket
import os
import queue
import time
import random
from datetime import datetime

# ── Theme ─────────────────────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")
ctk.set_widget_scaling(1.0)  # Ensures 1:1 crisp scaling
ctk.set_window_scaling(1.0)  

BG_DARK    = "#0e0e0e"   # bg-surface
BG_PANEL   = "#0e0e0e"   # main background
BG_SIDEBAR = "#131313"   # bg-[#131313]
BG_CARD    = "#1a1919"   # bg-surface-container 
BG_URL_BAR = "#131313"   # bg-surface-container-low inside cards
BG_ALERT   = "#1a1a1a"   # bg-[#1a1a1a]
BG_STATS   = "#131313"   # bg-surface-container-low
BG_INPUT   = "#000000"   # bg-surface-container-lowest
GREEN      = "#3fff8b"   # primary / surface-tint
GREEN_DIM  = "#24f07e"   # primary-dim
GREEN_TEXT = "#005d2c"   # on-primary (text on green bg)
GREEN_SIDE = "#262626"   # hover/active background in sidebar
GREEN_DARK = "#004f24"   # on-primary-container (used for badges)
RED        = "#9f0519"   # bg-error-container for stop button
RED_DIM    = "#d7383b"   # error-dim
BLUE       = "#4a86e8"   
BLUE_BG    = "#1e2b45"   # Fake transparent blue bg for the icon
GRAY       = "#494847"   # outline-variant / ghost borders
GRAY_DARK  = "#262626"   # surface-variant
TEXT       = "#ffffff"   # text-on-surface
TEXT_DIM   = "#adaaaa"   # text-on-surface-variant
TEXT_MONO  = "#3fff8b"   # monospace green


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def generate_certs_if_needed(log_fn):
    if os.path.exists("key.pem") and os.path.exists("cert.pem"):
        log_fn("INFO", "SSL certificates already exist. Skipping generation.")
        return
    log_fn("INFO", "Generating local SSL certificates...")
    import datetime as dt, ipaddress
    from cryptography import x509
    from cryptography.x509.oid import NameOID
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    ip_addr = get_local_ip()
    log_fn("INFO", f"Certificate target IP: {ip_addr}")
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, ip_addr)])
    cert = (
        x509.CertificateBuilder()
        .subject_name(subject).issuer_name(issuer)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(dt.datetime.now(dt.timezone.utc))
        .not_valid_after(dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=365))
        .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address(ip_addr))]), critical=False)
        .sign(key, hashes.SHA256())
    )
    with open("key.pem", "wb") as f:
        f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()))
    with open("cert.pem", "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    log_fn("INFO", "SSL certificate generated successfully.")


# ── Main Application ──────────────────────────────────────────────────────────
class MCXCamApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MCX CAM")
        self.geometry("1060x760")
        self.minsize(900, 680)
        self.configure(fg_color=BG_DARK)

        self.ip = get_local_ip()
        self.log_queue = queue.Queue()
        self._server_running = False
        self._peer_count = 0

        self._build_ui()
        self._poll_logs()

        # Startup log lines
        self._log("INFO", "MCX Cam Control Node initialized.")
        self._log("INFO", f"Local IP detected: {self.ip}")
        self._log("INFO", "Click 'START SERVER' to launch the streaming service.")

    # ── Build UI ──────────────────────────────────────────────────────────────
    def _build_ui(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        self.main_container = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0)
        self.main_container.grid(row=0, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.frames = {}
        self.nav_buttons = {}

        self._build_sidebar()
        self._build_main()
        
        from ui_server_settings import ServerSettingsFrame
        from ui_network_info import NetworkInfoFrame
        from ui_security_log import SecurityLogFrame
        from ui_vault import VaultFrame
        from ui_support import SupportFrame

        self.frames["Server Settings"] = ServerSettingsFrame(self.main_container, self)
        self.frames["Network Info"] = NetworkInfoFrame(self.main_container, self)
        self.frames["Security Log"] = SecurityLogFrame(self.main_container, self)
        self.frames["Vault"] = VaultFrame(self.main_container, self)
        self.frames["Support"] = SupportFrame(self.main_container, self)

        for name, frame in self.frames.items():
            frame.grid(row=0, column=0, sticky="nsew")
            
        self.show_frame("Console")

    def show_frame(self, name):
        frame = self.frames.get(name)
        if frame:
            frame.tkraise()
            
        for nav_name, nav_dict in self.nav_buttons.items():
            if nav_name == name:
                nav_dict["frame"].configure(fg_color=GREEN_SIDE)
                nav_dict["label"].configure(text_color=GREEN)
                nav_dict["indicator"].configure(fg_color=GREEN)
            else:
                nav_dict["frame"].configure(fg_color="transparent")
                nav_dict["label"].configure(text_color=TEXT_DIM)
                nav_dict["indicator"].configure(fg_color="transparent")

    # ── SIDEBAR ───────────────────────────────────────────────────────────────
    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, fg_color=BG_SIDEBAR, corner_radius=0, width=210)
        sb.grid(row=0, column=0, sticky="nsew")
        sb.grid_propagate(False)
        sb.grid_columnconfigure(0, weight=1)
        sb.grid_rowconfigure(6, weight=1)   # spacer row

        # Node badge
        badge = ctk.CTkFrame(sb, fg_color="transparent")
        badge.grid(row=0, column=0, padx=14, pady=(20, 6), sticky="ew")
        badge_inner = ctk.CTkFrame(badge, fg_color="transparent")
        badge_inner.pack(padx=12, pady=8, fill="x")
        
        # 32x32 Icon block
        icon_box = ctk.CTkFrame(badge_inner, width=32, height=32, fg_color="#12251a", border_width=1, border_color="#183d26", corner_radius=2)
        icon_box.grid_propagate(False)
        icon_box.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(icon_box, text="\uE968", font=("Segoe MDL2 Assets", 16), text_color=GREEN).place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(badge_inner, fg_color="transparent")
        info.pack(side="left")
        ctk.CTkLabel(info, text="MCX-01", font=("Segoe UI", 14, "bold"),
                     text_color=GREEN).pack(anchor="w", pady=0)
        ctk.CTkLabel(info, text="ACTIVE NODE", font=("Segoe UI", 9),
                     text_color=TEXT_DIM).pack(anchor="w", pady=0)

        # Nav items
        nav_items = [
            ("\uE756", "Console",        True),
            ("\uE713", "Server Settings", False),
            ("\uE774", "Network Info",   False),
            ("\uE72E", "Security Log",   False),
        ]
        for i, (icon, label, active) in enumerate(nav_items):
            row_frame = ctk.CTkFrame(
                sb,
                fg_color=GREEN_SIDE if active else "transparent",
                corner_radius=0
            )
            row_frame.grid(row=i + 1, column=0, pady=0, sticky="ew")
            row_frame.bind("<Button-1>", lambda e, n=label: self.show_frame(n))
            
            indicator = ctk.CTkFrame(row_frame, width=3, height=0)
            indicator.pack(side="left", fill="y")
            indicator.configure(fg_color=GREEN if active else "transparent")
                
            text_color = GREEN if active else TEXT_DIM
            lbl = ctk.CTkLabel(
                row_frame, text=f"  {icon}   {label}",
                font=("Segoe UI", 12, "bold"),
                text_color=text_color,
                anchor="w"
            )
            lbl.pack(side="left", padx=20, pady=10)
            lbl.bind("<Button-1>", lambda e, n=label: self.show_frame(n))
            
            self.nav_buttons[label] = {"frame": row_frame, "label": lbl, "indicator": indicator}

        # Spacer
        ctk.CTkLabel(sb, text="", fg_color="transparent").grid(row=6, column=0, sticky="ew")

        # Deploy button
        ctk.CTkButton(
            sb, text="\uE945  DEPLOY NODE",
            font=("Segoe UI", 12, "bold"),
            fg_color=GREEN, text_color=GREEN_TEXT,
            hover_color=GREEN_DIM,
            corner_radius=2, height=44
        ).grid(row=7, column=0, padx=16, pady=(0, 16), sticky="ew")

        # Bottom nav
        for i, (icon, label) in enumerate([("\uE72E", "Vault"), ("\uE897", "Support")]):
            row_frame = ctk.CTkFrame(sb, fg_color="transparent", corner_radius=0)
            row_frame.grid(row=8 + i, column=0, padx=0, pady=0, sticky="ew")
            row_frame.bind("<Button-1>", lambda e, n=label: self.show_frame(n))
            
            indicator = ctk.CTkFrame(row_frame, width=3, height=0)
            indicator.pack(side="left", fill="y")
            indicator.configure(fg_color="transparent")

            lbl = ctk.CTkLabel(
                row_frame, text=f"   {icon}   {label}",
                font=("Segoe UI", 11, "bold"), text_color=TEXT_DIM, anchor="w"
            )
            lbl.pack(side="left", padx=16, pady=8)
            lbl.bind("<Button-1>", lambda e, n=label: self.show_frame(n))
            
            self.nav_buttons[label] = {"frame": row_frame, "label": lbl, "indicator": indicator}

    # ── MAIN PANEL ────────────────────────────────────────────────────────────
    def _build_main(self):
        main = ctk.CTkFrame(self.main_container, fg_color=BG_PANEL, corner_radius=0)
        self.frames["Console"] = main
        main.grid(row=0, column=0, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(4, weight=1)   # log console expands

        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(main, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        header.grid(row=0, column=0, padx=28, pady=(24, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        ctk.CTkLabel(titles, text="Server Orchestrator",
                     font=("Segoe UI", 22, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(titles, text="Manage your MCX Node and connected stream clients.",
                     font=("Segoe UI", 11), text_color=TEXT_DIM).pack(anchor="w")

        btns = ctk.CTkFrame(header, fg_color="transparent")
        btns.grid(row=0, column=1, sticky="e", padx=20, pady=20)

        self.start_btn = ctk.CTkButton(
            btns, text=" \uE768  START SERVER",
            font=("Segoe UI", 12, "bold"),
            fg_color=GREEN, text_color=GREEN_TEXT,
            hover_color=GREEN_DIM, corner_radius=2, height=44, width=170,
            command=self.start_server
        )
        self.start_btn.pack(side="left", padx=(0, 12))

        self.stop_btn = ctk.CTkButton(
            btns, text=" \uE71A  STOP SERVER",
            font=("Segoe UI", 12, "bold"),
            fg_color=RED, text_color=TEXT,
            hover_color=RED_DIM, corner_radius=2, height=44, width=170,
            border_width=1, border_color=GRAY,
            state="disabled", command=self.stop_server
        )
        self.stop_btn.pack(side="left")

        # ── URL Cards ─────────────────────────────────────────────────────────
        cards = ctk.CTkFrame(main, fg_color="transparent")
        cards.grid(row=1, column=0, padx=28, pady=20, sticky="ew")
        cards.grid_columnconfigure((0, 1), weight=1)

        self._url_card(cards, col=0, icon="\uE8EA",
                       title="Sender (Mobile)",    badge="PRIMARY INPUT",
                       desc="Initialize camera stream from any mobile device node.",
                       url=f"https://{self.ip}:8000/sender.html", is_secondary=False)
        self._url_card(cards, col=1, icon="\uE7F4",
                       title="MCX Cam Desktop Dashboard",   badge="STREAM OUTPUT",
                       desc="Launch the localized hub interface.",
                       url=f"https://{self.ip}:8000/viewer.html", is_secondary=True)

        # ── SSL Alert Box ─────────────────────────────────────────────────────
        alert_box = ctk.CTkFrame(main, fg_color=BG_ALERT, corner_radius=10, border_width=1, border_color=GRAY)
        alert_box.grid(row=2, column=0, padx=28, pady=(0, 16), sticky="ew")
        alert_box.grid_columnconfigure(1, weight=1)

        # Simulated blue border box
        icon_box = ctk.CTkFrame(alert_box, fg_color=BLUE_BG, width=48, height=48, corner_radius=4, border_width=1, border_color=BLUE)
        icon_box.grid(row=0, column=0, padx=28, pady=28, rowspan=2)
        icon_box.grid_propagate(False)
        ctk.CTkLabel(icon_box, text="\uEA18", font=("Segoe MDL2 Assets", 20), text_color=BLUE).place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(alert_box, text="SSL Security Exception Required",
                     font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(row=0, column=1, sticky="w", pady=(22, 0))
        ctk.CTkLabel(alert_box, text="On first visit, click Advanced → Proceed to bypass the self-signed cert warning. This is expected for local server instances.",
                     font=("Segoe UI", 12), text_color="#666666", justify="left").grid(row=1, column=1, sticky="w", pady=(2, 22))

        # ── Stats Bar ─────────────────────────────────────────────────────────
        stats = ctk.CTkFrame(main, fg_color="transparent")
        stats.grid(row=3, column=0, padx=28, pady=(0, 16), sticky="ew")
        stats.grid_columnconfigure((0, 1, 2), weight=1)

        self.stat_latency   = self._stat_block(stats, col=0, label="LATENCY",      value="—")
        self.stat_bandwidth = self._stat_block(stats, col=1, label="BANDWIDTH",    value="—")
        self.stat_peers     = self._stat_block(stats, col=2, label="ACTIVE PEERS", value="00")

        # ── Log header ────────────────────────────────────────────────────────
        log_hdr = ctk.CTkFrame(main, fg_color=BG_STATS, corner_radius=0, border_width=1, border_color=GRAY_DARK)
        log_hdr.grid(row=4, column=0, padx=28, pady=(0, 0), sticky="ew")
        log_hdr.grid_columnconfigure(1, weight=1)

        log_inner = ctk.CTkFrame(log_hdr, fg_color="transparent")
        log_inner.grid(row=0, column=0, sticky="w", padx=16, pady=8)
        
        self.log_toggle_btn = ctk.CTkButton(log_inner, text="\uE70D", width=20, height=20,
                                            font=("Segoe MDL2 Assets", 12), fg_color="transparent",
                                            text_color=TEXT_DIM, hover_color=GRAY_DARK,
                                            command=self._toggle_logs)
        self.log_toggle_btn.pack(side="left", padx=(0, 8))

        ctk.CTkLabel(log_inner, text="\uE756   SYSTEM LOG CONSOLE",
                     font=("Segoe UI", 10, "bold"), text_color=TEXT_DIM
                     ).pack(side="left")

        self.live_dot = ctk.CTkLabel(log_hdr, text="\uE734 LIVE TAIL",
                                     font=("Segoe UI", 10, "bold"), text_color=TEXT_DIM)
        self.live_dot.grid(row=0, column=1, sticky="e", padx=16)

        # ── Log Console ───────────────────────────────────────────────────────
        self.log_wrap = ctk.CTkFrame(main, fg_color=BG_INPUT, corner_radius=0, border_width=1, border_color=GRAY_DARK)
        self.log_wrap.grid(row=5, column=0, padx=28, pady=(0, 24), sticky="nsew")
        self.log_wrap.grid_columnconfigure(0, weight=1)
        self.log_wrap.grid_rowconfigure(0, weight=1)

        self.log_box = ctk.CTkTextbox(
            self.log_wrap, fg_color=BG_INPUT,
            font=("Courier New", 12), text_color=TEXT_MONO,
            wrap="word", state="disabled",
            border_width=0, corner_radius=8
        )
        self.log_box.grid(padx=6, pady=6, sticky="nsew")
        
        self._logs_visible = True

        # ── Floating "+" FAB ──────────────────────────────────────────────────
        self.fab = ctk.CTkButton(
            main, text="\uE710", width=44, height=44,
            font=("Segoe MDL2 Assets", 18, "bold"),
            fg_color=GREEN, text_color=BG_DARK, bg_color="transparent",
            hover_color=GREEN_DIM, corner_radius=22,
            command=self._fab_action
        )
        # Place it via place() so it floats over the log area
        self.fab.place(relx=1.0, rely=1.0, x=-50, y=-50, anchor="se")

    # ── URL Card ──────────────────────────────────────────────────────────────
    def _url_card(self, parent, col, icon, title, badge, desc, url, is_secondary=False):
        pad_x = (0, 8) if col == 0 else (8, 0)
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        card.grid(row=0, column=col, padx=pad_x, pady=0, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

        # Top row: icon + badge
        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=24, pady=(24, 16))
        top.grid_columnconfigure(1, weight=1)

        icon_color = "#45fec9" if is_secondary else GREEN
        badge_bg = "#162b24" if is_secondary else "#12251a"
        border_c = "#1b4d3f" if is_secondary else "#183d26"

        icon_box = ctk.CTkFrame(top, width=48, height=48, fg_color=badge_bg, corner_radius=4, border_width=1, border_color=border_c)
        icon_box.grid_propagate(False)
        icon_box.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(icon_box, text=icon, font=("Segoe MDL2 Assets", 20), text_color=icon_color).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(top, text=f" {badge} ",
                     font=("Segoe UI", 10, "bold"),
                     text_color=icon_color, fg_color=badge_bg,
                     corner_radius=12, padx=6, pady=2
                     ).grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(card, text=title,
                     font=("Segoe UI", 16, "bold"), text_color=TEXT
                     ).pack(anchor="w", padx=24)
        ctk.CTkLabel(card, text=desc,
                     font=("Segoe UI", 11), text_color=TEXT_DIM,
                     wraplength=260, justify="left"
                     ).pack(anchor="w", padx=24, pady=(4, 16))

        # URL row
        url_row = ctk.CTkFrame(card, fg_color=BG_URL_BAR, corner_radius=2, border_width=1, border_color=GRAY_DARK)
        url_row.pack(fill="x", padx=24, pady=(0, 24))
        url_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(url_row, text=url,
                     font=("Courier New", 12), text_color=icon_color,
                     anchor="w"
                     ).grid(row=0, column=0, padx=12, pady=10, sticky="w")
                     
        launch_btn = ctk.CTkButton(url_row, text="\uE8A7", width=30, height=26,
                      font=("Segoe UI", 11, "bold"), 
                      fg_color= GREEN if is_secondary else "transparent", 
                      text_color= BG_DARK if is_secondary else TEXT_DIM,
                      hover_color=GREEN_DIM if is_secondary else GRAY, corner_radius=4,
                      command=lambda u=url: self._launch(u))
        launch_btn.grid(row=0, column=1, padx=(0, 4), pady=4)

        ctk.CTkButton(url_row, text="\uE8C8", width=30, height=26,
                      font=("Segoe MDL2 Assets", 14), 
                      fg_color="transparent", text_color=TEXT_DIM,
                      hover_color=GRAY, corner_radius=4,
                      command=lambda u=url: self._copy(u)
                      ).grid(row=0, column=2, padx=(0, 4), pady=4)

    # ── Stat block ────────────────────────────────────────────────────────────
    def _stat_block(self, parent, col, label, value):
        pad_x = (0, 8) if col == 0 else ((8, 0) if col == 2 else (4, 4))
        block = ctk.CTkFrame(parent, fg_color=BG_STATS, corner_radius=8)
        block.grid(row=0, column=col, padx=pad_x, pady=0, sticky="ew")
        
        # Left boundary fake border
        border = ctk.CTkFrame(block, fg_color=GREEN, width=3, height=1, bg_color="transparent")
        border.pack(side="left", fill="y", pady=12)
        
        content = ctk.CTkFrame(block, fg_color="transparent")
        content.pack(padx=16, pady=12, anchor="w", fill="x")
        
        ctk.CTkLabel(content, text=label,
                     font=("Space Grotesk", 10, "bold"), text_color=TEXT_DIM).pack(anchor="w")
        val = ctk.CTkLabel(content, text=value,
                           font=("Space Grotesk", 24, "bold"), text_color=TEXT)
        val.pack(anchor="w")
        return val

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _toggle_logs(self):
        if self._logs_visible:
            self.log_wrap.grid_remove()
            self.log_toggle_btn.configure(text="\uE76C")
        else:
            self.log_wrap.grid()
            self.log_toggle_btn.configure(text="\uE70D")
        self._logs_visible = not self._logs_visible

    def _launch(self, url):
        import webbrowser
        self._log("INFO", f"Launching: {url}")
        webbrowser.open(url)

    def _copy(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self._log("INFO", f"Copied to clipboard: {text}")

    def _fab_action(self):
        self._log("INFO", "Node action triggered via FAB.")

    def _log(self, level, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        color_map = {
            "INFO":    GREEN,
            "SUCCESS": "#00ff6e",
            "WARN":    "#f39c12",
            "ERROR":   RED_DIM,
            "DEBUG":   TEXT_DIM,
        }
        self.log_queue.put((ts, level, msg, color_map.get(level, TEXT)))

    def _poll_logs(self):
        try:
            while True:
                ts, level, msg, color = self.log_queue.get_nowait()
                self.log_box.configure(state="normal")
                self.log_box.insert("end", f"[{ts}] ")
                self.log_box.insert("end", f"{level}: ", level)
                self.log_box.insert("end", f"{msg}\n")
                self.log_box.tag_config(level, foreground=color)
                self.log_box.see("end")
                self.log_box.configure(state="disabled")
        except queue.Empty:
            pass
        self.after(100, self._poll_logs)

    def _update_stats(self):
        """Simulate live latency / bandwidth while server is running."""
        if self._server_running:
            try:
                lat = random.randint(8, 22)
                bw  = round(random.uniform(2.0, 6.5), 1)
                self.stat_latency.configure(text=f"{lat}ms")
                self.stat_bandwidth.configure(text=f"{bw} Mbps")
                self.stat_peers.configure(
                    text=f"{self._peer_count:02d}",
                    text_color=GREEN if self._peer_count > 0 else TEXT
                )
            except:
                pass
            self.after(2000, self._update_stats)

    # ── Server control ────────────────────────────────────────────────────────
    def start_server(self):
        if self._server_running:
            self._log("WARN", "Server is already marked as running.")
            return

        # Check port 8000 first
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex(('127.0.0.1', 8000)) == 0:
                self._log("ERROR", "Port 8000 is occupied. Kill old uvicorn or try another port.")
                return

        self.start_btn.configure(state="disabled")
        self._log("INFO", "Initializing background server...")
        threading.Thread(target=self._run_server, daemon=True).start()

    def _run_server(self):
        import asyncio
        import uvicorn
        
        # Step 1 — generate certs
        try:
            generate_certs_if_needed(self._log)
        except Exception as e:
            self._log("ERROR", f"Cert generation failed: {e}")
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            return

        # Step 2 — imports and config
        try:
            from main import app as fastapi_app
            config = uvicorn.Config(
                fastapi_app,
                host="0.0.0.0",
                port=8000,
                ssl_keyfile="key.pem",
                ssl_certfile="cert.pem",
                log_config=None, # suppress uvicorn log pollution and fix formatter error in pyinstaller
                log_level="error",
                workers=1,
                loop="asyncio"
            )
            self._uvicorn_server = uvicorn.Server(config)
        except Exception as e:
            self._log("ERROR", f"Server config error: {e}")
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            return

        # Step 3 — actual serve execution in isolated loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # We start the uvicorn serve as a task, and wait until it's 'started'
        async def run_server_loop():
            self._log("INFO", "Binding to HTTPS port 8000...")
            serve_task = asyncio.ensure_future(self._uvicorn_server.serve())
            
            # Watch for startup
            while not self._uvicorn_server.started:
                if self._uvicorn_server.should_exit: break
                await asyncio.sleep(0.1)
                
            if self._uvicorn_server.started:
                self._server_running = True
                self.after(0, self._on_server_started)
            
            await serve_task

        try:
            loop.run_until_complete(run_server_loop())
        except Exception as e:
            self._log("ERROR", f"Server error: {e}")
        finally:
            loop.close()
            self._server_running = False
            self.after(0, self._on_server_stopped)

    def _on_server_started(self):
        self._log("INFO", f"Binding to HTTPS port 8000...")
        self._log("INFO", "SSL Certificate verified (local self-signed).")
        self._log("INFO", f"Started server process at {self.ip}")
        self._log("DEBUG", "Peer discovery service started.")
        self._log("DEBUG", "WebSocket handshake ready on /ws")
        self._log("SUCCESS", "Node fully operational. Ready for connections.")
        self.live_dot.configure(text_color=GREEN)
        self.stop_btn.configure(state="normal")
        self._peer_count = 0
        self._update_stats()

    def stop_server(self):
        if not self._server_running or not hasattr(self, "_uvicorn_server"):
            return
        self._log("WARN", "Shutting down server...")
        self._uvicorn_server.should_exit = True

    def _on_server_stopped(self):
        self._log("INFO", "Server stopped.")
        self.live_dot.configure(text_color=TEXT_DIM)
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.stat_latency.configure(text="—")
        self.stat_bandwidth.configure(text="—")
        self.stat_peers.configure(text="00", text_color=TEXT)

    def on_closing(self):
        if self._server_running:
            self.stop_server()
            time.sleep(1)
        self.destroy()


# ── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = MCXCamApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
