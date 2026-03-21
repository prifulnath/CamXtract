import ctypes
try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

import customtkinter as ctk
import socket
import os
import time

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

class MCXCamApp(ctk.CTk):
    def _get_res(self, path):
        import sys, os
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, path)
        return os.path.abspath(path)

    def __init__(self):
        super().__init__()
        self.title("MCX CAM")
        self.geometry("1060x760")
        self.minsize(900, 680)
        self.configure(fg_color=BG_DARK)
        
        ico_path = self._get_res("app/mcx_logo.ico")
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

    def _set_appwindow(self):
        try:
            import ctypes
            GWL_EXSTYLE = -20
            WS_EX_APPWINDOW = 0x00040000
            WS_EX_TOOLWINDOW = 0x00000080
            hwnd = ctypes.windll.user32.GetParent(self.winfo_id())
            style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            style = style & ~WS_EX_TOOLWINDOW
            style = style | WS_EX_APPWINDOW
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style)
            self.wm_withdraw()
            self.wm_deiconify()
        except Exception:
            pass

        self.main_container = ctk.CTkFrame(self, fg_color=BG_PANEL, corner_radius=0)
        self.main_container.grid(row=1, column=1, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(0, weight=1)

        self.frames = {}
        
        # Load external decoupled UI modules
        from ui.ui_menu import MenuFrame
        from ui.ui_console import ConsoleFrame
        from ui.ui_server_settings import ServerSettingsFrame
        from ui.ui_network_info import NetworkInfoFrame
        from ui.ui_security_log import SecurityLogFrame
        from ui.ui_vault import VaultFrame
        from ui.ui_support import SupportFrame

        self.sidebar = MenuFrame(self, self)
        
        self.frames["Console"] = ConsoleFrame(self.main_container, self)
        self.frames["Server Settings"] = ServerSettingsFrame(self.main_container, self)
        self.frames["Network Info"] = NetworkInfoFrame(self.main_container, self)
        self.frames["Security Log"] = SecurityLogFrame(self.main_container, self)
        self.frames["Vault"] = VaultFrame(self.main_container, self)
        self.frames["Support"] = SupportFrame(self.main_container, self)

        for name, frame in self.frames.items():
            frame.grid(row=0, column=0, sticky="nsew")
        
        # Wire up the Deploy Configuration button inside Server Settings panel
        self.frames["Server Settings"].deploy_btn.configure(command=self._update_server_name)
            
        self._update_server_name(initial=True)
        self.show_frame("Console")

        self.frames["Console"].log("INFO", "MCX Cam Control Node initialized.")
        self.frames["Console"].log("INFO", f"Local IP detected: {self.ip}")
        self.frames["Console"].log("INFO", "Click 'START SERVER' to launch the streaming service.")

    def _update_server_name(self, event=None, initial=False):
        self.frames["Server Settings"].save_config()
        new_name = self.frames["Server Settings"].server_name_entry.get().strip().upper()
        if not new_name: new_name = "MCX-01"
        self.node_badge_label.configure(text=new_name)
        if not initial:
            self.frames["Console"].log("SUCCESS", f"Configuration deployed. Node identity applied: {new_name}")

    def show_frame(self, name):
        frame = self.frames.get(name)
        if frame:
            frame.tkraise()
            
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
        self.title_bar.grid_columnconfigure(1, weight=1)

        branding = ctk.CTkFrame(self.title_bar, fg_color="transparent")
        branding.grid(row=0, column=0, padx=24, pady=10, sticky="w")
        
        icon_box = ctk.CTkFrame(branding, width=28, height=28, fg_color="transparent", corner_radius=0)
        icon_box.pack_propagate(False)
        icon_box.pack(side="left", padx=(0, 10))
        
        logo_path = self._get_res("app/mcx_logo.png")
        if os.path.exists(logo_path):
            import tkinter as tk
            self.title_logo = tk.PhotoImage(file=logo_path)
            ctk.CTkLabel(icon_box, text="", image=self.title_logo).pack()
        else:
            ctk.CTkLabel(icon_box, text="\uE968", font=("Segoe MDL2 Assets", 14), text_color=GREEN).pack()
        
        title_lbl = ctk.CTkLabel(branding, text="MCX CAM", font=("Space Grotesk", 18, "bold"), text_color=GREEN)
        title_lbl.pack(side="left")

        controls = ctk.CTkFrame(self.title_bar, fg_color="transparent")
        controls.grid(row=0, column=2, padx=16, sticky="e")

        def minimize():
            self.iconify()
        
        def maximize():
            if self.state() == "zoomed":
                self.state("normal")
            else:
                self.state("zoomed")

        def close():
            self.on_closing()

        ctk.CTkButton(controls, text="\uE921", font=("Segoe MDL2 Assets", 11), width=32, height=32, fg_color="transparent", text_color=TEXT_DIM, hover_color=GRAY_DARK, command=minimize).pack(side="left", padx=4)
        ctk.CTkButton(controls, text="\uE922", font=("Segoe MDL2 Assets", 10), width=32, height=32, fg_color="transparent", text_color=TEXT_DIM, hover_color=GRAY_DARK, command=maximize).pack(side="left", padx=4)
        ctk.CTkButton(controls, text="\uE8BB", font=("Segoe MDL2 Assets", 11), width=32, height=32, fg_color="transparent", text_color=TEXT_DIM, hover_color="#c42b1c", command=close).pack(side="left", padx=4)

        def start_move(event):
            self.x = event.x
            self.y = event.y

        def do_move(event):
            deltax = event.x - self.x
            deltay = event.y - self.y
            x = self.winfo_x() + deltax
            y = self.winfo_y() + deltay
            self.geometry(f"+{x}+{y}")

        self.title_bar.bind("<Button-1>", start_move)
        self.title_bar.bind("<B1-Motion>", do_move)
        branding.bind("<Button-1>", start_move)
        branding.bind("<B1-Motion>", do_move)
        icon_box.bind("<Button-1>", start_move)
        icon_box.bind("<B1-Motion>", do_move)
        title_lbl.bind("<Button-1>", start_move)
        title_lbl.bind("<B1-Motion>", do_move)

    def on_closing(self):
        try:
            if hasattr(self, "frames") and self.frames.get("Console") and getattr(self.frames["Console"], "_server_running", False):
                self.frames["Console"].stop_server()
                time.sleep(1)
        except Exception:
            pass
        os._exit(0)

if __name__ == "__main__":
    app = MCXCamApp()
    app.protocol("WM_DELETE_WINDOW", app.on_closing)
    app.mainloop()
