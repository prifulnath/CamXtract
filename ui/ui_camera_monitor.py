import customtkinter as ctk
import webbrowser
import threading
import socket
import time

# Colors
BG_PANEL   = "#0e0e0e"
BG_CARD    = "#1a1919"
BG_HIGHEST = "#262626"
BG_DARK    = "#000000"
GREEN      = "#3fff8b"
GREEN_DIM  = "#24f07e"
GREEN_TEXT = "#005d2c"
PURPLE     = "#b48bff"
PURPLE_BG  = "#1e1630"
PURPLE_BDR = "#3b2a6a"
AMBER      = "#f5a623"
AMBER_BG   = "#2a1f0e"
TEXT       = "#ffffff"
TEXT_DIM   = "#adaaaa"
GRAY       = "#2a2a2a"


def _try_import_webview2():
    """Import WebView2 lazily — returns the class or None on failure."""
    try:
        from tkwebview2.tkwebview2 import WebView2, have_runtime
        if not have_runtime():
            return None, "Edge WebView2 runtime not found."
        return WebView2, None
    except Exception as e:
        return None, str(e)


class CameraMonitorFrame(ctk.CTkFrame):
    def __init__(self, master, app_ref, *args, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, corner_radius=0, *args, **kwargs)
        self.app_ref = app_ref

        self._webview_widget   = None   # embedded WebView2 widget
        self._webview_ready    = False  # WebView2 initialised and URL loaded
        self._server_was_on    = False
        self._wv_class, self._wv_err = _try_import_webview2()

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # ── Header ─────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=28, pady=(24, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        title_row = ctk.CTkFrame(header, fg_color="transparent")
        title_row.pack(fill="x")
        title_row.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(title_row, text="Camera Monitor",
                     font=("Space Grotesk", 36, "bold"), text_color=TEXT
                     ).grid(row=0, column=0, sticky="w")

        badge = ctk.CTkFrame(title_row, fg_color=BG_HIGHEST, corner_radius=4)
        badge.grid(row=0, column=1, sticky="e")
        self._live_dot = ctk.CTkLabel(badge, text="●", font=("Segoe UI", 10),
                                       text_color=TEXT_DIM)
        self._live_dot.pack(side="left", padx=(8, 2), pady=4)
        self._live_lbl = ctk.CTkLabel(badge, text="OFFLINE",
                                       font=("Courier New", 10, "bold"), text_color=TEXT_DIM)
        self._live_lbl.pack(side="left", padx=(0, 8), pady=4)

        ctk.CTkLabel(header, text="Live WebRTC feed from the active sender device.",
                     font=("Space Grotesk", 14), text_color=TEXT_DIM
                     ).pack(anchor="w", pady=(4, 0))

        # ── Body ───────────────────────────────────────────────────────────────
        self._body = ctk.CTkFrame(self, fg_color="transparent")
        self._body.grid(row=1, column=0, padx=28, pady=(16, 8), sticky="nsew")
        self._body.grid_columnconfigure(0, weight=1)
        self._body.grid_rowconfigure(0, weight=1)

        # ── Offline placeholder ─────────────────────────────────────────────
        self._ph = ctk.CTkFrame(self._body, fg_color=BG_CARD, corner_radius=12,
                                border_width=1, border_color=GRAY)
        self._ph.grid(row=0, column=0, sticky="nsew")
        self._ph.grid_columnconfigure(0, weight=1)
        self._ph.grid_rowconfigure(0, weight=1)

        ph_inner = ctk.CTkFrame(self._ph, fg_color="transparent")
        ph_inner.place(relx=0.5, rely=0.5, anchor="center")

        self._ph_icon = ctk.CTkLabel(ph_inner, text="\uE722",
                                      font=("Segoe MDL2 Assets", 52), text_color="#333333")
        self._ph_icon.pack(pady=(0, 16))
        self._ph_title = ctk.CTkLabel(ph_inner, text="No Signal",
                                       font=("Space Grotesk", 22, "bold"), text_color="#444444")
        self._ph_title.pack()
        self._ph_desc = ctk.CTkLabel(
            ph_inner,
            text="Start the server and connect a sender device." if self._wv_class
                 else f"WebView2 unavailable: {self._wv_err}",
            font=("Space Grotesk", 13), text_color="#333333")
        self._ph_desc.pack(pady=(8, 24))
        ctk.CTkButton(ph_inner, text="\uE756  GO TO CONSOLE",
                      font=("Space Grotesk", 11, "bold"),
                      fg_color=GREEN, text_color=GREEN_TEXT, hover_color=GREEN_DIM,
                      height=40, corner_radius=4,
                      command=self._go_console).pack()

        # ── WebView2 container (shown when server is on) ────────────────────
        # We use a plain tk.Frame because WebView2 needs a native HWND parent
        import tkinter as tk
        self._wv_container = tk.Frame(self._body, bg="#000000")
        # (hidden initially)

        # ── Bottom controls ────────────────────────────────────────────────────
        ctrl = ctk.CTkFrame(self, fg_color="transparent")
        ctrl.grid(row=2, column=0, padx=28, pady=(0, 18), sticky="ew")

        btn_kw = dict(font=("Space Grotesk", 11, "bold"), height=38, corner_radius=4)

        self._refresh_btn = ctk.CTkButton(
            ctrl, text="\uE72C  RECONNECT", width=150,
            fg_color=BG_CARD, text_color=TEXT_DIM, hover_color=BG_HIGHEST,
            border_width=1, border_color=GRAY,
            command=self._reconnect, **btn_kw)
        self._refresh_btn.pack(side="left", padx=(0, 8))

        ctk.CTkButton(ctrl, text="\uE8A7  OPEN IN BROWSER", width=190,
                      fg_color=PURPLE_BG, text_color=PURPLE,
                      hover_color=PURPLE_BDR, border_width=1, border_color=PURPLE_BDR,
                      command=self._open_browser, **btn_kw).pack(side="left", padx=(0, 8))

        ctk.CTkButton(ctrl, text="\uE756  CONSOLE", width=130,
                      fg_color=BG_CARD, text_color=TEXT_DIM, hover_color=BG_HIGHEST,
                      border_width=1, border_color=GRAY,
                      command=self._go_console, **btn_kw).pack(side="left")

        # Start polling
        self.after(1000, self._poll)

    # ── Helpers ────────────────────────────────────────────────────────────────

    def _get_url(self):
        console = self.app_ref.frames.get("Console")
        port = console._server_port if console else 8000
        return f"https://{self.app_ref.ip}:{port}/viewer.html"

    def _server_running(self):
        c = self.app_ref.frames.get("Console")
        return c._server_running if c else False

    def _port_open(self, port):
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            return False

    # ── Poll loop ──────────────────────────────────────────────────────────────

    def _poll(self):
        running = self._server_running()

        if running:
            self._live_dot.configure(text_color=GREEN)
            self._live_lbl.configure(text="LIVE ", text_color=GREEN)

            if not self._server_was_on:
                self._server_was_on = True
                # Wait for port to actually open, then load
                console = self.app_ref.frames.get("Console")
                port = console._server_port if console else 8000
                threading.Thread(target=self._wait_and_load, args=(port,),
                                 daemon=True).start()
        else:
            self._live_dot.configure(text_color=TEXT_DIM)
            self._live_lbl.configure(text="OFFLINE", text_color=TEXT_DIM)

            if self._server_was_on:
                self._server_was_on = False
                self._show_placeholder("Server stopped.")

        self.after(1200, self._poll)

    def _wait_and_load(self, port):
        """Background: wait for port then load URL into WebView2 on main thread."""
        for _ in range(30):          # up to 15 s
            if self._port_open(port):
                self.after(0, self._show_webview)
                return
            time.sleep(0.5)
        # Timed out — show fallback
        self.after(0, lambda: self._show_placeholder("Server started but port not reachable."))

    # ── WebView2 management ────────────────────────────────────────────────────

    def _show_webview(self):
        """Called on main thread once port is open."""
        if not self._wv_class:
            self._open_browser()
            return

        url = self._get_url()

        # Show the container, flush layout so winfo_width/height are accurate
        self._ph.grid_remove()
        self._wv_container.grid(row=0, column=0, sticky="nsew")
        self.update_idletasks()   # force geometry pass BEFORE reading dimensions

        if self._webview_widget is None:
            self._create_webview(url)
        else:
            try:
                self._webview_widget.load_url(url)
            except Exception:
                self._create_webview(url)

    def _create_webview(self, url: str):
        """Instantiate the WebView2 widget inside the container."""
        try:
            if self._webview_widget:
                try:
                    self._webview_widget.destroy()
                except Exception:
                    pass
                self._webview_widget = None

            w = max(self._wv_container.winfo_width(),  640)
            h = max(self._wv_container.winfo_height(), 400)

            # IMPORTANT: pass url='' so WebView2 doesn't navigate yet.
            # We must wire the ServerCertificateErrorDetected handler FIRST
            # before any navigation happens — otherwise the SSL cert error
            # fires before our handler subscribes (race condition → white screen).
            wv = self._wv_class(self._wv_container, width=w, height=h, url="")
            wv.pack(fill="both", expand=True)
            self._webview_widget = wv
            self._webview_ready = True

            # Poll until CoreWebView2 is ready (wv.core is set by tkwebview2's
            # __load_core handler). Using events risks a race: the event may have
            # already fired by the time we subscribe—leaving a permanent white page.
            _nav_url = url

            def _poll_core(wv=wv, url=_nav_url):
                try:
                    core = wv.core
                except Exception:
                    core = None

                if core is None:
                    # Not ready yet — try again in 100 ms
                    self.after(100, _poll_core)
                    return

                # CoreWebView2 is ready — wire cert bypass then navigate
                try:
                    def _on_cert_error(s2, args):
                        try:
                            args.Action = args.Action.__class__(1)  # AlwaysAllow
                        except Exception:
                            pass
                    core.ServerCertificateErrorDetected += _on_cert_error
                    core.Navigate(url)
                except Exception:
                    try:
                        wv.load_url(url)  # fallback via pywebview path
                    except Exception:
                        pass

            self.after(100, _poll_core)

        except Exception as e:
            self._show_placeholder(f"WebView2 error: {e}")

    def _show_placeholder(self, msg: str = ""):
        self._wv_container.grid_remove()
        self._ph.grid(row=0, column=0, sticky="nsew")
        if msg:
            self._ph_desc.configure(text=msg)

    # ── Button actions ─────────────────────────────────────────────────────────

    def _go_console(self):
        self.app_ref.show_frame("Console")
        self.app_ref.sidebar.set_active("Console")

    def _open_browser(self):
        if self._server_running():
            webbrowser.open(self._get_url())

    def _reconnect(self):
        """Reload the WebView2 widget with the current URL."""
        if not self._server_running():
            return
        if self._webview_widget and self._webview_ready:
            try:
                self._webview_widget.load_url(self._get_url())
                return
            except Exception:
                pass
        # Widget not ready — force refresh cycle
        self._server_was_on = False
        self._show_placeholder("Reconnecting…")
        console = self.app_ref.frames.get("Console")
        port = console._server_port if console else 8000
        threading.Thread(target=self._wait_and_load, args=(port,), daemon=True).start()

    # Called by gui.py (kept for API compatibility)
    def on_panel_shown(self): pass
    def on_panel_hidden(self): pass
