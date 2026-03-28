import ctypes
try:
    _windll = getattr(ctypes, 'windll', None)
    if _windll:
        _windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import sys
from typing import Any
import customtkinter as ctk
import socket
import os

# Colors
BG_DARK    = "#0e0e0e"
BG_PANEL   = "#0e0e0e"
BG_SIDEBAR = "#131313"
GREEN      = "#3fff8b"
TEXT_DIM   = "#adaaaa"
GRAY_DARK  = "#262626"

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

class CamXtractApp(ctk.CTk):
    def _get_res(self, path):
        """Resolve a resource path for both dev and PyInstaller environments."""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(getattr(sys, '_MEIPASS'), path)
        return os.path.abspath(path)

    def __init__(self):
        super().__init__()
        self.title("CamXtract")
        self.geometry("1060x760")
        self.minsize(900, 680)
        self.configure(fg_color=BG_DARK)

        ico_path = self._get_res("app/camxtract_logo.ico")
        if os.path.exists(ico_path):
            try:
                self.iconbitmap(ico_path)
            except Exception:
                pass

        self.ip = get_local_ip()
        self._build_ui()

    def _build_ui(self):
        self.overrideredirect(True)
        self.after(10, self._set_appwindow)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_title_bar()
        self._show_splash()          # ← appears immediately

    # ── Splash screen ──────────────────────────────────────────────────────────

    def _show_splash(self):
        """Full-area loading screen shown while panels are initialised."""
        self._splash = ctk.CTkFrame(self, fg_color=BG_DARK, corner_radius=0)
        self._splash.grid(row=1, column=0, columnspan=2, sticky="nsew")

        center = ctk.CTkFrame(self._splash, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        logo_path = self._get_res("app/camxtract_logo.png")
        if os.path.exists(logo_path):
            import tkinter as tk
            _logo = tk.PhotoImage(file=logo_path)
            lbl = ctk.CTkLabel(center, text="", image=_logo)
            lbl._img = _logo  # keep reference
            lbl.pack(pady=(0, 20))
        else:
            ctk.CTkLabel(center, text="\uE968",
                         font=("Segoe MDL2 Assets", 56), text_color=GREEN).pack(pady=(0, 20))

        ctk.CTkLabel(center, text="CamXtract",
                     font=("Space Grotesk", 30, "bold"), text_color=GREEN).pack()
        ctk.CTkLabel(center, text="VISUAL INTELLIGENCE CONTROL NODE",
                     font=("Space Grotesk", 10, "bold"), text_color=TEXT_DIM).pack(pady=(4, 28))

        self._splash_status = ctk.CTkLabel(center, text="Initialising…",
                                           font=("Space Grotesk", 11), text_color=TEXT_DIM)
        self._splash_status.pack()

        self._splash_bar = ctk.CTkProgressBar(center, width=240,
                                               progress_color=GREEN, fg_color="#1a1a1a",
                                               corner_radius=4, height=4)
        self._splash_bar.set(0)
        self._splash_bar.pack(pady=(12, 0))

    def _splash_update(self, text, pct):
        if hasattr(self, "_splash_status"):
            self._splash_status.configure(text=text)
            self._splash_bar.set(pct)
        self.update_idletasks()

    def _hide_splash(self):
        if hasattr(self, "_splash"):
            self._splash.destroy()
            del self._splash

    # ── Deferred panel initialisation ──────────────────────────────────────────

    def _set_appwindow(self):
        try:
            GWL_EXSTYLE     = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW= 0x00000080
            _windll = getattr(ctypes, 'windll', None)
            if _windll:
                hwnd  = _windll.user32.GetParent(self.winfo_id())
                style = _windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                style = style & ~WS_EX_TOOLWINDOW | WS_EX_APPWINDOW
                _windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            self.wm_withdraw()
            self.wm_deiconify()
        except Exception:
            pass

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.main_container = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0)
        self.main_container.grid(row=1, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.frames = {}      # instantiated frames
        self._frame_defs = {  # lazy definitions (module, class)
            "Console":          ("ui.ui_console",           "ConsoleFrame"),
            "Server Settings":  ("ui.ui_server_settings",   "ServerSettingsFrame"),
            "Camera Controls":  ("ui.ui_camera_controls",   "CameraControlsFrame"),
            "Network Info":     ("ui.ui_network_info",       "NetworkInfoFrame"),
            "Security Log":     ("ui.ui_security_log",       "SecurityLogFrame"),
            "Vault":            ("ui.ui_vault",              "VaultFrame"),
            "Support":          ("ui.ui_support",            "SupportFrame"),
            # Camera Monitor last — heaviest (loads .NET CLR via tkwebview2)
            "Camera Monitor":   ("ui.ui_camera_monitor",     "CameraMonitorFrame"),
        }

        # Build sidebar (lightweight)
        self._splash_update("Loading…", 0.3)
        from ui.ui_menu import MenuFrame
        self.sidebar = MenuFrame(self, self)

        # Eagerly load only Console (the initial view)
        self.after(20, self._boot_console)

    def _instantiate_frame(self, name):
        """Import and create a single frame on demand."""
        if name in self.frames:
            return self.frames[name]
        module_path, class_name = self._frame_defs[name]
        try:
            import importlib
            mod = importlib.import_module(module_path)
            cls = getattr(mod, class_name)
            frame = cls(self.main_container, self)
            frame.grid(row=0, column=0, sticky="nsew")
            self.frames[name] = frame
        except Exception as e:
            err_frame = ctk.CTkFrame(self.main_container, fg_color="#0e0e0e", corner_radius=0)
            ctk.CTkLabel(err_frame, text=f"Error loading {name}:\n{e}",
                         font=("Courier New", 11), text_color="#ff716c",
                         wraplength=600, justify="left").pack(padx=30, pady=30, anchor="nw")
            err_frame.grid(row=0, column=0, sticky="nsew")
            self.frames[name] = err_frame
        return self.frames[name]

    def _boot_console(self):
        """Create Console, wire it up, then hide splash and show it."""
        self._splash_update("Starting Console…", 0.8)
        self._instantiate_frame("Console")
        self._instantiate_frame("Server Settings")  # needed for deploy_btn + auto-start
        self.after(20, self._finish_loading)

    def _finish_loading(self):
        self._splash_update("Ready!", 1.0)

        # Wire up Deploy Configuration button
        try:
            self.frames["Server Settings"].deploy_btn.configure(command=self._update_server_name)
        except Exception:
            pass

        self._update_server_name(initial=True)

        con = self.frames.get("Console")
        if con:
            con.log("INFO", "CamXtract Control Node initialized.")
            con.log("INFO", f"Local IP detected: {self.ip}")
            con.log("INFO", "Click 'START SERVER' to launch the streaming service.")

        ss = self.frames.get("Server Settings")
        auto_start = ss.ui_elements.get("Auto-start Engine") if ss else None
        if auto_start and str(auto_start.get()) in ("1", "True", "true"):
            if con:
                con.log("INFO", "Auto-start enabled. Launching server...")
            self.after(500, lambda: self.frames["Console"].start_server())

        # Remove splash and show Console
        self.after(150, self._reveal_app)

    def _reveal_app(self):
        self._hide_splash()
        self.show_frame("Console")

    # ── Helpers ────────────────────────────────────────────────────────────────

    @property
    def _server_running(self):
        console = self.frames.get("Console")
        return console._server_running if console else False

    def _update_server_name(self, event=None, initial=False):
        self.frames["Server Settings"].save_config()
        new_name = self.frames["Server Settings"].server_name_entry.get().strip().upper()
        if not new_name:
            new_name = "CamXtract-01"
        self.node_badge_label.configure(text=new_name)
        if not initial:
            self.frames["Console"].log("SUCCESS",
                f"Configuration deployed. Node identity applied: {new_name}")

    def show_frame(self, name):
        prev = getattr(self, "_active_frame_name", None)
        if prev == "Camera Monitor" and name != "Camera Monitor":
            cam = self.frames.get("Camera Monitor")
            if cam and hasattr(cam, "on_panel_hidden"):
                cam.on_panel_hidden()

        # Lazy-instantiate the panel on first click
        if name not in self.frames and name in self._frame_defs:
            self._instantiate_frame(name)

        frame = self.frames.get(name)
        if frame:
            frame.tkraise()

        if name == "Camera Monitor":
            cam = self.frames.get("Camera Monitor")
            if cam and hasattr(cam, "on_panel_shown"):
                cam.on_panel_shown()

        self._active_frame_name = name

        for nav_name, nav_dict in getattr(self, "nav_buttons", {}).items():
            if nav_name == name:
                nav_dict["frame"].configure(fg_color="#16281f")
                nav_dict["label"].configure(text_color=GREEN)
                nav_dict["indicator"].configure(fg_color=GREEN)
            else:
                nav_dict["frame"].configure(fg_color="transparent")
                nav_dict["label"].configure(text_color=TEXT_DIM)
                nav_dict["indicator"].configure(fg_color="transparent")

    def _build_title_bar(self):
        self.title_bar = ctk.CTkFrame(self, fg_color="#0e0e0e", height=48, corner_radius=0)
        self.title_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.title_bar.grid_propagate(False)
        self.title_bar.grid_columnconfigure(1, weight=1)  # spacer column stretches
        self.title_bar.grid_columnconfigure(2, weight=0)  # window controls — fixed width

        branding = ctk.CTkFrame(self.title_bar, fg_color="transparent")
        branding.grid(row=0, column=0, padx=24, pady=10, sticky="w")

        icon_box = ctk.CTkFrame(branding, width=28, height=28,
                                fg_color="transparent", corner_radius=0)
        icon_box.pack_propagate(False)
        icon_box.pack(side="left", padx=(0, 10))

        logo_path = self._get_res("app/camxtract_logo.png")
        if os.path.exists(logo_path):
            import tkinter as tk
            self.title_logo = tk.PhotoImage(file=logo_path)
            ctk.CTkLabel(icon_box, text="", image=self.title_logo).pack()
        else:
            ctk.CTkLabel(icon_box, text="\uE968",
                         font=("Segoe MDL2 Assets", 14), text_color=GREEN).pack()

        title_lbl = ctk.CTkLabel(branding, text="CamXtract",
                                  font=("Space Grotesk", 18, "bold"), text_color=GREEN)
        title_lbl.pack(side="left")

        controls = ctk.CTkFrame(self.title_bar, fg_color="transparent")
        controls.grid(row=0, column=2, padx=(16, 0), sticky="e")

        def minimize():
            # iconify() doesn't work with overrideredirect — use Win32 directly
            _windll = getattr(ctypes, 'windll', None)
            if _windll:
                hwnd = _windll.user32.GetParent(self.winfo_id())
                _windll.user32.ShowWindow(hwnd, 6)  # SW_MINIMIZE
        def maximize():
            self.state("normal") if self.state() == "zoomed" else self.state("zoomed")
        def close():     self.on_closing()

        btn_style: dict[str, Any] = dict(font=("Segoe MDL2 Assets", 10), width=46, height=48,
                                          fg_color="transparent", text_color="#cccccc", corner_radius=0)
        ctk.CTkButton(controls, text="\uE921", hover_color="#2a2a2a",
                      command=minimize, **btn_style).pack(side="left")
        ctk.CTkButton(controls, text="\uE922", hover_color="#2a2a2a",
                      command=maximize, **btn_style).pack(side="left")
        ctk.CTkButton(controls, text="\uE8BB", hover_color="#c42b1c",
                      command=close,    **btn_style).pack(side="left")

        def start_move(e): self.x = e.x; self.y = e.y
        def do_move(e):
            self.geometry(f"+{self.winfo_x()+e.x-self.x}+{self.winfo_y()+e.y-self.y}")

        for w in (self.title_bar, branding, icon_box, title_lbl):
            w.bind("<Button-1>", start_move)
            w.bind("<B1-Motion>", do_move)

    def on_closing(self):
        try:
            console = self.frames.get("Console") if hasattr(self, "frames") else None
            if console and hasattr(console, "_uvicorn_server") and console._uvicorn_server:
                # Signal uvicorn to stop — don't wait for it, os._exit cleans up
                console._uvicorn_server.should_exit = True
                console._uvicorn_server.force_exit = True
        except Exception:
            pass
        os._exit(0)

if __name__ == "__main__":
    app = CamXtractApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
