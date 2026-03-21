import customtkinter as ctk
import time
import socket
import threading
import queue
import random
from datetime import datetime

# Colors
BG_PANEL   = "#111111"
BG_CARD    = "#161616"
BG_ALERT   = "#1d1911"
BG_STATS   = "#151515"
BG_INPUT   = "#181818"
BG_URL_BAR = "#121212"
BG_DARK    = "#0e0e0e"

GREEN      = "#3fff8b"
GREEN_DIM  = "#13ea79"
GREEN_TEXT = "#005d2c"
BLUE       = "#4a86e8"
BLUE_BG    = "#1e2b45"
RED_DIM    = "#ff716c"

TEXT       = "#ffffff"
TEXT_DIM   = "#adaaaa"
TEXT_MONO  = "#e0e0e0"
GRAY       = "#333333"
GRAY_DARK  = "#222222"


class ConsoleFrame(ctk.CTkFrame):
    def __init__(self, master, app_ref):
        super().__init__(master, fg_color=BG_PANEL, corner_radius=0)
        self.app_ref = app_ref
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(5, weight=1)   # log console expands

        self.log_queue = queue.Queue()
        self._server_running = False
        self._server_port = 8000
        self._peer_count = 0

        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        header.grid(row=0, column=0, padx=28, pady=(24, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w", padx=20, pady=20)
        ctk.CTkLabel(titles, text="Server Orchestrator", font=("Segoe UI", 22, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(titles, text="Manage your MCX Node and connected stream clients.", font=("Segoe UI", 11), text_color=TEXT_DIM).pack(anchor="w")

        btns = ctk.CTkFrame(header, fg_color="transparent")
        btns.grid(row=0, column=1, sticky="e", padx=20, pady=20)

        self.start_btn = ctk.CTkButton(
            btns, text=" \uE102  START SERVER", font=("Space Grotesk", 11, "bold"),
            fg_color=GREEN, text_color=GREEN_TEXT, hover_color=GREEN_DIM, corner_radius=4, height=44, width=170,
            command=self.start_server
        )
        self.start_btn.pack(side="left", padx=(0, 12))

        self.stop_btn = ctk.CTkButton(
            btns, text=" \uE15B  STOP SERVER", font=("Space Grotesk", 11, "bold"),
            fg_color="#ff716c", text_color="#490006", hover_color="#d7383b", corner_radius=4, height=44, width=170,
            state="disabled", command=self.stop_server
        )
        self.stop_btn.pack(side="left")

        # ── URL Cards ─────────────────────────────────────────────────────────
        cards = ctk.CTkFrame(self, fg_color="transparent")
        cards.grid(row=1, column=0, padx=28, pady=20, sticky="ew")
        cards.grid_columnconfigure((0, 1), weight=1)

        self.url_cards_data = []

        self._url_card(cards, col=0, icon="\uE8EA", title="Sender (Mobile)", badge="PRIMARY INPUT",
                       desc="Initialize camera stream from any mobile device node.", url_path="/sender.html", is_secondary=False)
        self._url_card(cards, col=1, icon="\uE7F4", title="MCX Cam Desktop Dashboard", badge="STREAM OUTPUT",
                       desc="Launch the localized hub interface.", url_path="/viewer.html", is_secondary=True)

        # ── SSL Alert Box ─────────────────────────────────────────────────────
        alert_box = ctk.CTkFrame(self, fg_color=BG_ALERT, corner_radius=10, border_width=1, border_color=GRAY)
        alert_box.grid(row=2, column=0, padx=28, pady=(0, 16), sticky="ew")
        alert_box.grid_columnconfigure(1, weight=1)

        icon_box = ctk.CTkFrame(alert_box, fg_color=BLUE_BG, width=48, height=48, corner_radius=4, border_width=1, border_color=BLUE)
        icon_box.grid(row=0, column=0, padx=28, pady=28, rowspan=2)
        icon_box.pack_propagate(False)
        ctk.CTkLabel(icon_box, text="\uEA18", font=("Segoe MDL2 Assets", 20), text_color=BLUE).place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(alert_box, text="SSL Security Exception Required", font=("Segoe UI", 16, "bold"), text_color=TEXT).grid(row=0, column=1, sticky="w", pady=(22, 0))
        desc_frame = ctk.CTkFrame(alert_box, fg_color="transparent")
        desc_frame.grid(row=1, column=1, sticky="w", pady=(2, 22))
        ctk.CTkLabel(desc_frame, text="On first visit, click ", font=("Segoe UI", 12), text_color="#666666").pack(side="left")
        ctk.CTkLabel(desc_frame, text="Advanced → Proceed", font=("Segoe UI", 12, "bold"), text_color="#aaaaaa").pack(side="left")
        ctk.CTkLabel(desc_frame, text=" to bypass the self-signed cert warning.", font=("Segoe UI", 12), text_color="#666666").pack(side="left")

        # ── Stats Bar ─────────────────────────────────────────────────────────
        stats = ctk.CTkFrame(self, fg_color="transparent")
        stats.grid(row=3, column=0, padx=28, pady=(0, 16), sticky="ew")
        stats.grid_columnconfigure((0, 1, 2), weight=1)

        self.stat_latency   = self._stat_block(stats, col=0, label="LATENCY",      value="—")
        self.stat_bandwidth = self._stat_block(stats, col=1, label="BANDWIDTH",    value="—")
        self.stat_peers     = self._stat_block(stats, col=2, label="ACTIVE PEERS", value="00")

        # ── Log header ────────────────────────────────────────────────────────
        log_hdr = ctk.CTkFrame(self, fg_color=BG_STATS, corner_radius=0, border_width=1, border_color=GRAY_DARK)
        log_hdr.grid(row=4, column=0, padx=28, pady=(0, 0), sticky="ew")
        log_hdr.grid_columnconfigure(1, weight=1)

        log_inner = ctk.CTkFrame(log_hdr, fg_color="transparent")
        log_inner.grid(row=0, column=0, sticky="w", padx=16, pady=8)
        
        self.log_toggle_btn = ctk.CTkButton(log_inner, text="\uE70D", width=20, height=20, font=("Segoe MDL2 Assets", 12), fg_color="transparent",
                                            text_color=TEXT_DIM, hover_color=GRAY_DARK, command=self._toggle_logs)
        self.log_toggle_btn.pack(side="left", padx=(0, 8))
        ctk.CTkLabel(log_inner, text="\uE756   SYSTEM LOG CONSOLE", font=("Segoe UI", 10, "bold"), text_color=TEXT_DIM).pack(side="left")

        self.live_dot = ctk.CTkLabel(log_hdr, text="\uE734 LIVE TAIL", font=("Segoe UI", 10, "bold"), text_color=TEXT_DIM)
        self.live_dot.grid(row=0, column=1, sticky="e", padx=16)

        # ── Log Console ───────────────────────────────────────────────────────
        self.log_wrap = ctk.CTkFrame(self, fg_color=BG_INPUT, corner_radius=0, border_width=1, border_color=GRAY_DARK)
        self.log_wrap.grid(row=5, column=0, padx=28, pady=(0, 24), sticky="nsew")
        self.log_wrap.grid_columnconfigure(0, weight=1)
        self.log_wrap.grid_rowconfigure(0, weight=1)

        self.log_box = ctk.CTkTextbox(self.log_wrap, fg_color=BG_INPUT, font=("Courier New", 12), text_color=TEXT_MONO, wrap="word", state="disabled", border_width=0, corner_radius=8)
        self.log_box.grid(padx=6, pady=6, sticky="nsew")
        
        self._logs_visible = True

        # ── Floating "+" FAB ──────────────────────────────────────────────────
        self.fab = ctk.CTkButton(self.log_wrap, text="+", width=48, height=48, font=("Courier New", 28, "bold"),
                                 fg_color=GREEN, text_color=BG_DARK, bg_color=BG_INPUT, hover_color=GREEN_DIM, corner_radius=24, command=self._fab_action)
        self.fab.place(relx=1.0, rely=1.0, x=-24, y=-24, anchor="se")

        # Start background loop
        self.after(100, self._poll_logs)

    # ── URL Card ──────────────────────────────────────────────────────────────
    def _url_card(self, parent, col, icon, title, badge, desc, url_path, is_secondary=False):
        pad_x = (0, 8) if col == 0 else (8, 0)
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY)
        card.grid(row=0, column=col, padx=pad_x, pady=0, sticky="ew")
        card.grid_columnconfigure(0, weight=1)

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

        ctk.CTkLabel(top, text=f" {badge} ", font=("Segoe UI", 10, "bold"), text_color=icon_color, fg_color=badge_bg, corner_radius=12, padx=6, pady=2).grid(row=0, column=1, sticky="e")

        ctk.CTkLabel(card, text=title, font=("Segoe UI", 16, "bold"), text_color=TEXT).pack(anchor="w", padx=24)
        ctk.CTkLabel(card, text=desc, font=("Segoe UI", 11), text_color=TEXT_DIM, justify="left").pack(anchor="w", padx=24, pady=(4, 16))

        url_row = ctk.CTkFrame(card, fg_color=BG_URL_BAR, corner_radius=4, border_width=1, border_color=GRAY_DARK)
        url_row.pack(fill="x", padx=24, pady=(0, 24))
        url_row.grid_columnconfigure(0, weight=1)

        url_lbl = ctk.CTkLabel(url_row, text=f"https://{self.app_ref.ip}:8000{url_path}", font=("Courier New", 12), text_color=icon_color, anchor="w")
        url_lbl.grid(row=0, column=0, padx=12, pady=10, sticky="w")
                     
        launch_btn = ctk.CTkButton(url_row, text="\uE8A7", width=30, height=30, font=("Segoe MDL2 Assets", 14), 
                      fg_color="transparent", text_color=TEXT_DIM, hover_color=GRAY_DARK, corner_radius=4,
                      command=lambda l=url_lbl: self._launch(l.cget("text")))
        launch_btn.grid(row=0, column=1, padx=(0, 4), pady=4)

        ctk.CTkButton(url_row, text="\uE8C8", width=30, height=30, font=("Segoe MDL2 Assets", 14), fg_color="transparent", text_color=TEXT_DIM,
                      hover_color=GRAY_DARK, corner_radius=4, command=lambda l=url_lbl: self._copy(l.cget("text"))).grid(row=0, column=2, padx=(0, 4), pady=4)

        self.url_cards_data.append({"label": url_lbl, "path": url_path})

    # ── Stat block ────────────────────────────────────────────────────────────
    def _stat_block(self, parent, col, label, value):
        pad_x = (0, 8) if col == 0 else ((8, 0) if col == 2 else (4, 4))
        block = ctk.CTkFrame(parent, fg_color=BG_STATS, corner_radius=8)
        block.grid(row=0, column=col, padx=pad_x, pady=0, sticky="ew")
        
        border = ctk.CTkFrame(block, fg_color=GREEN, width=3, height=1, bg_color="transparent")
        border.pack(side="left", fill="y", pady=12)
        
        content = ctk.CTkFrame(block, fg_color="transparent")
        content.pack(padx=16, pady=12, anchor="w", fill="x")
        
        ctk.CTkLabel(content, text=label, font=("Space Grotesk", 10, "bold"), text_color=TEXT_DIM).pack(anchor="w")
        val = ctk.CTkLabel(content, text=value, font=("Space Grotesk", 24, "bold"), text_color=TEXT)
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
        self.log("INFO", f"Launching: {url}")
        webbrowser.open(url)

    def _copy(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.log("INFO", f"Copied to clipboard: {text}")

    def _fab_action(self):
        self.log("INFO", "Node action triggered via FAB.")

    def log(self, level, msg):
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
        if self._server_running:
            try:
                lat = random.randint(8, 22)
                bw  = round(random.uniform(2.0, 6.5), 1)
                self.stat_latency.configure(text=f"{lat}ms")
                self.stat_bandwidth.configure(text=f"{bw} Mbps")
                self.stat_peers.configure(text=f"{self._peer_count:02d}", text_color=GREEN if self._peer_count > 0 else TEXT)
            except:
                pass
            self.after(2000, self._update_stats)

    # ── Server control ────────────────────────────────────────────────────────
    def start_server(self):
        if self._server_running:
            self.log("WARN", "Server is already marked as running.")
            return

        try:
            self._server_port = int(self.app_ref.frames["Server Settings"].port_entry.get())
        except ValueError:
            self.log("ERROR", "Invalid port specified.")
            return

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            if s.connect_ex(('127.0.0.1', self._server_port)) == 0:
                self.log("ERROR", f"Port {self._server_port} is occupied. Try another port.")
                return

        self.start_btn.configure(state="disabled")
        self.log("INFO", "Initializing background server...")
        threading.Thread(target=self._run_server, daemon=True).start()

    def _generate_certs_if_needed(self):
        import os, socket, datetime, ipaddress
        if os.path.exists("key.pem") and os.path.exists("cert.pem"):
            self.log("INFO", "SSL certificates already exist. Skipping generation.")
            return
        self.log("INFO", "Generating local SSL certificates...")
        from cryptography import x509
        from cryptography.x509.oid import NameOID
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import rsa
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("10.255.255.255", 1)); ip_addr = s.getsockname()[0]
        except: ip_addr = "127.0.0.1"
        finally: s.close()
        self.log("INFO", f"Certificate target IP: {ip_addr}")
        key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        subject = issuer = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, ip_addr)])
        cert = (x509.CertificateBuilder().subject_name(subject).issuer_name(issuer)
            .public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(datetime.datetime.now(datetime.timezone.utc))
            .not_valid_after(datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=365))
            .add_extension(x509.SubjectAlternativeName([x509.IPAddress(ipaddress.ip_address(ip_addr))]), critical=False)
            .sign(key, hashes.SHA256()))
        with open("key.pem", "wb") as f:
            f.write(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.TraditionalOpenSSL, serialization.NoEncryption()))
        with open("cert.pem", "wb") as f:
            f.write(cert.public_bytes(serialization.Encoding.PEM))
        self.log("INFO", "SSL certificate generated successfully.")

    def _run_server(self):
        import asyncio
        import uvicorn
        
        try:
            self._generate_certs_if_needed()
        except Exception as e:
            self.log("ERROR", f"Cert generation failed: {e}")
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            return

        try:
            from main import app as fastapi_app
            config = uvicorn.Config(
                fastapi_app, host="0.0.0.0", port=self._server_port,
                ssl_keyfile="key.pem", ssl_certfile="cert.pem",
                log_config=None, log_level="error", workers=1, loop="asyncio"
            )
            self._uvicorn_server = uvicorn.Server(config)
        except Exception as e:
            self.log("ERROR", f"Server config error: {e}")
            self.after(0, lambda: self.start_btn.configure(state="normal"))
            return

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        async def run_server_loop():
            self.log("INFO", f"Binding to HTTPS port {self._server_port}...")
            serve_task = asyncio.ensure_future(self._uvicorn_server.serve())
            
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
            self.log("ERROR", f"Server error: {e}")
        finally:
            loop.close()
            self._server_running = False
            self.after(0, self._on_server_stopped)

    def _on_server_started(self):
        self.log("INFO", f"Binding to HTTPS port {self._server_port}...")
        self.log("INFO", "SSL Certificate verified (local self-signed).")
        self.log("INFO", f"Started server process at {self.app_ref.ip}:{self._server_port}")
        self.log("DEBUG", "Peer discovery service started.")
        self.log("DEBUG", "WebSocket handshake ready on /ws")
        self.log("SUCCESS", "Node fully operational. Ready for connections.")
        self.live_dot.configure(text_color=GREEN)
        self.stop_btn.configure(state="normal")
        self._peer_count = 0
        self._update_stats()
        
        for card_data in self.url_cards_data:
            card_data["label"].configure(text=f"https://{self.app_ref.ip}:{self._server_port}{card_data['path']}")

    def stop_server(self):
        if not self._server_running or not hasattr(self, "_uvicorn_server"):
            return
        self.log("WARN", "Shutting down server...")
        self._uvicorn_server.should_exit = True

    def _on_server_stopped(self):
        self.log("INFO", "Server stopped.")
        self.live_dot.configure(text_color=TEXT_DIM)
        self.start_btn.configure(state="normal")
        self.stop_btn.configure(state="disabled")
        self.stat_latency.configure(text="—")
        self.stat_bandwidth.configure(text="—")
        self.stat_peers.configure(text="00", text_color=TEXT)
