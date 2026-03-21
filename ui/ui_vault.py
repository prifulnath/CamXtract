import customtkinter as ctk
import os
from datetime import datetime, timezone
from tkinter import filedialog

BG_PANEL   = "#0e0e0e"
BG_CARD    = "#1a1919"
BG_CARD_L  = "#131313"
BG_HIGHEST = "#262626"
GREEN      = "#3fff8b"
GREEN_DIM  = "#24f07e"
GREEN_TXT  = "#005d2c"
TEXT       = "#ffffff"
TEXT_DIM   = "#adaaaa"
GRAY       = "#494847"
GRAY_DARK  = "#333333"
RED        = "#ff716c"
BLUE       = "#4a86e8"


class VaultFrame(ctk.CTkFrame):
    def __init__(self, master, app_ref, *args, **kwargs):
        super().__init__(master, fg_color=BG_PANEL, corner_radius=0, *args, **kwargs)
        self.app_ref = app_ref
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._masked = {}   # key → bool (True = masked)
        self._values = {}   # key → real value label widget

        self._build_header()

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.grid(row=1, column=0, padx=28, pady=20, sticky="nsew")
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)
        content.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(content, fg_color="transparent")
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        right = ctk.CTkFrame(content, fg_color="transparent")
        right.grid(row=0, column=1, sticky="nsew", padx=(10, 0))

        self._build_secrets(left)
        self._build_access_control(right)

    def _build_header(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, padx=28, pady=(24, 0), sticky="ew")
        header.grid_columnconfigure(0, weight=1)

        titles = ctk.CTkFrame(header, fg_color="transparent")
        titles.grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(titles, text="Secure Vault", font=("Space Grotesk", 32, "bold"), text_color=TEXT).pack(anchor="w")
        ctk.CTkLabel(titles, text="Encrypted credential store for sensitive infrastructure secrets.",
                     font=("Space Grotesk", 12), text_color=TEXT_DIM).pack(anchor="w")

        # Vault status badge
        has_certs = os.path.exists("key.pem") and os.path.exists("cert.pem")
        badge_color = "#12251a" if has_certs else "#252018"
        badge_text  = "\u25CF  SEALED" if has_certs else "\u25CB  EMPTY"
        badge_col   = GREEN if has_certs else TEXT_DIM

        btns = ctk.CTkFrame(header, fg_color="transparent")
        btns.grid(row=0, column=1, sticky="e")
        badge_f = ctk.CTkFrame(btns, fg_color=badge_color, corner_radius=6, border_width=1, border_color=GRAY)
        badge_f.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(badge_f, text=badge_text, font=("Space Grotesk", 11, "bold"), text_color=badge_col).pack(padx=14, pady=8)

        ctk.CTkButton(btns, text="\uE896  EXPORT VAULT", font=("Space Grotesk", 11, "bold"),
                      height=36, fg_color=GREEN, text_color=GREEN_TXT, hover_color=GREEN_DIM,
                      command=self._export_vault).pack(side="left")

    def _build_secrets(self, parent):
        sec_head = ctk.CTkFrame(parent, fg_color="transparent")
        sec_head.pack(fill="x", pady=(0, 14))
        ctk.CTkLabel(sec_head, text="\u25CF ", font=("Segoe UI", 12), text_color=GREEN).pack(side="left")
        ctk.CTkLabel(sec_head, text="STORED SECRETS", font=("Space Grotesk", 10, "bold"), text_color=GREEN).pack(side="left")

        # SSL Certificate entry (real)
        self._vault_entry(parent, "SSL_CERT", "\uEA18", "SSL Certificate", self._read_cert_fingerprint(),
                          "cert.pem", expires=self._read_cert_expiry())

        # SSL Private Key entry
        self._vault_entry(parent, "SSL_KEY", "\uE8D7", "SSL Private Key", self._read_key_snippet(),
                          "key.pem")

        # API Key placeholder
        self._vault_entry(parent, "API_KEY", "\uE8FB", "API Access Token",
                          "Not configured", "N/A", locked=True)

        # TURN credentials placeholder
        self._vault_entry(parent, "TURN_CRED", "\uE81E", "TURN/STUN Credentials",
                          "Not configured", "N/A", locked=True)

    def _vault_entry(self, parent, key, icon, title, value, source, expires=None, locked=False):
        card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY_DARK)
        card.pack(fill="x", pady=(0, 12))

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=16, pady=(16, 8))

        icon_box = ctk.CTkFrame(top, fg_color="#12251a" if not locked else BG_HIGHEST,
                                 width=36, height=36, corner_radius=4)
        icon_box.pack_propagate(False)
        icon_box.pack(side="left", padx=(0, 12))
        ctk.CTkLabel(icon_box, text=icon, font=("Segoe MDL2 Assets", 14),
                     text_color=GREEN if not locked else TEXT_DIM).place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(top, fg_color="transparent")
        info.pack(side="left", fill="x", expand=True)
        ctk.CTkLabel(info, text=title, font=("Space Grotesk", 12, "bold"), text_color=TEXT if not locked else TEXT_DIM).pack(anchor="w")
        src_lbl = source if len(source) < 32 else source[:30] + "..."
        ctk.CTkLabel(info, text=f"Source: {src_lbl}", font=("Space Grotesk", 9), text_color=TEXT_DIM).pack(anchor="w")

        if expires:
            ctk.CTkLabel(info, text=f"Expires: {expires}", font=("Space Grotesk", 9), text_color=TEXT_DIM).pack(anchor="w")

        # Action buttons
        if not locked:
            btn_row = ctk.CTkFrame(top, fg_color="transparent")
            btn_row.pack(side="right")

            self._masked[key] = True

            reveal_btn = ctk.CTkButton(btn_row, text="\uE7B3", width=28, height=28,
                                        font=("Segoe MDL2 Assets", 12), fg_color="transparent",
                                        text_color=TEXT_DIM, hover_color=BG_HIGHEST, corner_radius=4)
            reveal_btn.pack(side="left", padx=2)

            ctk.CTkButton(btn_row, text="\uE8C8", width=28, height=28,
                          font=("Segoe MDL2 Assets", 12), fg_color="transparent",
                          text_color=TEXT_DIM, hover_color=BG_HIGHEST, corner_radius=4,
                          command=lambda v=value: self._copy(v)).pack(side="left", padx=2)

        # Value display
        val_row = ctk.CTkFrame(card, fg_color=BG_CARD_L, corner_radius=4)
        val_row.pack(fill="x", padx=16, pady=(0, 16))

        display = "•" * min(32, len(value)) if (not locked and value != "Not configured") else value
        val_lbl = ctk.CTkLabel(val_row, text=display, font=("Courier New", 11), text_color=GREEN if not locked else TEXT_DIM, anchor="w")
        val_lbl.pack(fill="x", padx=10, pady=8)

        self._values[key] = (val_lbl, value)

        if not locked and value != "Not configured":
            reveal_btn.configure(command=lambda k=key: self._toggle_reveal(k))

    def _toggle_reveal(self, key):
        lbl, real_val = self._values[key]
        self._masked[key] = not self._masked[key]
        if self._masked[key]:
            lbl.configure(text="•" * min(32, len(real_val)))
        else:
            lbl.configure(text=real_val)

    def _copy(self, value):
        self.clipboard_clear()
        self.clipboard_append(value)

    def _read_cert_fingerprint(self):
        if not os.path.exists("cert.pem"):
            return "Not configured"
        try:
            from cryptography import x509
            from cryptography.hazmat.primitives import hashes
            import binascii
            with open("cert.pem", "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())
            fp = binascii.hexlify(cert.fingerprint(hashes.SHA256())).decode().upper()
            return ":".join(fp[i:i+2] for i in range(0, min(32, len(fp)), 2))
        except:
            return "Error reading cert"

    def _read_key_snippet(self):
        if not os.path.exists("key.pem"):
            return "Not configured"
        try:
            with open("key.pem", "r") as f:
                lines = f.readlines()
            return (lines[1][:28] + "...") if len(lines) > 1 else "RSA Private Key"
        except:
            return "Error reading key"

    def _read_cert_expiry(self):
        if not os.path.exists("cert.pem"):
            return None
        try:
            from cryptography import x509
            with open("cert.pem", "rb") as f:
                cert = x509.load_pem_x509_certificate(f.read())
            exp = cert.not_valid_after_utc
            days = (exp - datetime.now(timezone.utc)).days
            return f"{exp.strftime('%Y-%m-%d')} ({days}d remaining)"
        except:
            return None

    def _build_access_control(self, parent):
        ctk.CTkLabel(parent, text="ACCESS CONTROL", font=("Space Grotesk", 10, "bold"), text_color=GREEN).pack(anchor="w", pady=(0, 14))

        for role, desc, perms in [
            ("ADMIN",  "Full system access", ["Read", "Write", "Deploy", "Vault"]),
            ("SENDER", "Camera input node",  ["Stream Only"]),
            ("VIEWER", "Read-only monitor",  ["View Stream"]),
        ]:
            card = ctk.CTkFrame(parent, fg_color=BG_CARD, corner_radius=8, border_width=1, border_color=GRAY_DARK)
            card.pack(fill="x", pady=(0, 12))
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=16, pady=16)
            ctk.CTkLabel(inner, text=role, font=("Space Grotesk", 13, "bold"), text_color=GREEN).pack(anchor="w")
            ctk.CTkLabel(inner, text=desc, font=("Space Grotesk", 10), text_color=TEXT_DIM).pack(anchor="w", pady=(2, 8))
            perm_row = ctk.CTkFrame(inner, fg_color="transparent")
            perm_row.pack(anchor="w")
            for p in perms:
                b = ctk.CTkFrame(perm_row, fg_color="#12251a", corner_radius=4)
                b.pack(side="left", padx=(0, 6))
                ctk.CTkLabel(b, text=p, font=("Space Grotesk", 9, "bold"), text_color=GREEN).pack(padx=8, pady=3)

    def _export_vault(self):
        lines = ["MCX CAM — Vault Export\n" + "="*40]
        for key, (lbl, real_val) in self._values.items():
            lines.append(f"{key}: {real_val}")
        path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt")],
            title="Export Vault"
        )
        if path:
            with open(path, "w") as f:
                f.write("\n".join(lines))
