import tkinter as tk
from tkinter import ttk, messagebox
import threading
from monitor_api import MonitorController

# Modern Dark Theme Palette
BG_COLOR = "#0f1117"
PANEL_BG = "#181b24"
PANEL_BORDER = "#252936"
TEXT_COLOR = "#e2e8f0"
TEXT_MUTED = "#94a3b8"
ACCENT_COLOR = "#3b82f6"
ACCENT_HOVER = "#2563eb"
SUCCESS_COLOR = "#10b981"

SMART_MODES = {
    0x00: "Standard",
    0x02: "Movie",
    0x03: "Game / FPS",
    0x05: "Reader / Low Blue Light"
}

COLOR_PRESETS = {
    0x05: "Standard",
    0x08: "Warm",
    0x0B: "Cool",
    0x0C: "Custom RGB"
}

INPUT_SOURCES = [
    ("DisplayPort 1", 0x0F),
    ("DisplayPort 2", 0x10),
    ("HDMI 1", 0x11),
    ("HDMI 2", 0x12)
]

class DisplayCommanderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RM Display Commander — Xiaomi 34\" Control Hub")
        self.root.geometry("640x780")
        self.root.minsize(580, 720)
        self.root.configure(bg=BG_COLOR)

        self.ctl = MonitorController()
        self._init_styles()
        self._build_ui()
        self._load_live_values()

    def _init_styles(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure(".", background=BG_COLOR, foreground=TEXT_COLOR)
        style.configure("TLabel", background=BG_COLOR, foreground=TEXT_COLOR, font=("Segoe UI", 10))
        style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), foreground="#60a5fa")
        style.configure("Sub.TLabel", font=("Segoe UI", 8), foreground=TEXT_MUTED)
        style.configure("TCombobox", fieldbackground=PANEL_BG, background=PANEL_BORDER, foreground=TEXT_COLOR)
        style.configure("Horizontal.TScale", background=PANEL_BG, troughcolor="#232733", sliderlength=18)

    def _build_ui(self):
        # Header banner
        hdr = tk.Frame(self.root, bg=BG_COLOR, pady=10, padx=20)
        hdr.pack(fill="x")

        title_lbl = tk.Label(hdr, text="RM Display Commander", font=("Segoe UI", 16, "bold"), fg="#ffffff", bg=BG_COLOR)
        title_lbl.pack(anchor="w")

        sub_lbl = tk.Label(hdr, text=f"Active Hardware: {self.ctl.description} | Xiaomi Mi Curved 34\"", font=("Segoe UI", 9), fg=TEXT_MUTED, bg=BG_COLOR)
        sub_lbl.pack(anchor="w")

        # Safety Banner
        safe_badge = tk.Frame(hdr, bg="#064e3b", padx=10, pady=3, highlightbackground="#059669", highlightthickness=1)
        safe_badge.pack(anchor="w", pady=(6, 0))
        tk.Label(safe_badge, text="PROTECTION ACTIVE: VCP 0xD6 HARD-LOCKED (OSD Bug Immune)", font=("Segoe UI", 8, "bold"), fg="#a7f3d0", bg="#064e3b").pack()

        # Main scrollable canvas container
        main_frame = tk.Frame(self.root, bg=BG_COLOR, padx=16, pady=4)
        main_frame.pack(fill="both", expand=True)

        # Panel 1: Image & Luminance
        p1 = self._create_card(main_frame, "IMAGE & LUMINANCE")
        self.brightness_var, self.b_val_lbl = self._create_slider_row(p1, "Brightness", 0, 100, self._on_brightness_change)
        self.contrast_var, self.c_val_lbl = self._create_slider_row(p1, "Contrast", 0, 100, self._on_contrast_change)
        self.sharpness_var, self.s_val_lbl = self._create_slider_row(p1, "Sharpness", 0, 100, self._on_sharpness_change)
        self.black_level_var, self.bl_val_lbl = self._create_slider_row(p1, "Black Equalizer", 0, 100, self._on_black_level_change)
        self.dcr_var, self.dcr_val_lbl = self._create_slider_row(p1, "Dynamic Luminance (DCR)", 0, 100, self._on_dcr_change)

        # Panel 2: Gaming & Color Modes
        p2 = self._create_card(main_frame, "GAMING & SMARTMODES")

        # SmartMode Dropdown
        sm_row = tk.Frame(p2, bg=PANEL_BG, pady=4)
        sm_row.pack(fill="x")
        tk.Label(sm_row, text="SmartMode Preset:", font=("Segoe UI", 10), fg=TEXT_COLOR, bg=PANEL_BG).pack(side="left")
        self.smart_mode_combo = ttk.Combobox(sm_row, values=list(SMART_MODES.values()), state="readonly", width=22)
        self.smart_mode_combo.pack(side="right")
        self.smart_mode_combo.bind("<<ComboboxSelected>>", self._on_smartmode_select)

        # Color Preset Dropdown
        col_row = tk.Frame(p2, bg=PANEL_BG, pady=4)
        col_row.pack(fill="x")
        tk.Label(col_row, text="Color Temperature:", font=("Segoe UI", 10), fg=TEXT_COLOR, bg=PANEL_BG).pack(side="left")
        self.color_preset_combo = ttk.Combobox(col_row, values=list(COLOR_PRESETS.values()), state="readonly", width=22)
        self.color_preset_combo.pack(side="right")
        self.color_preset_combo.bind("<<ComboboxSelected>>", self._on_color_preset_select)

        # RGB Gains
        self.r_var, self.r_lbl = self._create_slider_row(p2, "Red Gain", 0, 100, lambda v: self._on_rgb_change())
        self.g_var, self.g_lbl = self._create_slider_row(p2, "Green Gain", 0, 100, lambda v: self._on_rgb_change())
        self.b_gain_var, self.bg_lbl = self._create_slider_row(p2, "Blue Gain", 0, 100, lambda v: self._on_rgb_change())

        # FreeSync Toggle Button
        fs_row = tk.Frame(p2, bg=PANEL_BG, pady=6)
        fs_row.pack(fill="x")
        tk.Label(fs_row, text="AMD FreeSync Premium:", font=("Segoe UI", 10), fg=TEXT_COLOR, bg=PANEL_BG).pack(side="left")
        self.fs_btn = tk.Button(fs_row, text="ENABLED", font=("Segoe UI", 9, "bold"), bg="#059669", fg="#ffffff", padx=12, pady=2, relief="flat", command=self._toggle_freesync)
        self.fs_btn.pack(side="right")

        # Panel 3: 1-Click Input Switcher
        p3 = self._create_card(main_frame, "INPUT SWITCHER")
        inp_btn_frame = tk.Frame(p3, bg=PANEL_BG, pady=4)
        inp_btn_frame.pack(fill="x")
        for label, val in INPUT_SOURCES:
            b = tk.Button(inp_btn_frame, text=label, font=("Segoe UI", 9), bg="#252936", fg=TEXT_COLOR, activebackground=ACCENT_COLOR, activeforeground="#ffffff", relief="flat", padx=10, pady=6, command=lambda v=val, l=label: self._switch_input(v, l))
            b.pack(side="left", expand=True, fill="x", padx=3)

    def _create_card(self, parent, title):
        card = tk.Frame(parent, bg=PANEL_BG, padx=14, pady=10, highlightbackground=PANEL_BORDER, highlightthickness=1)
        card.pack(fill="x", pady=6)
        tk.Label(card, text=title, font=("Segoe UI", 9, "bold"), fg="#60a5fa", bg=PANEL_BG).pack(anchor="w", pady=(0, 6))
        return card

    def _create_slider_row(self, parent, label_text, min_v, max_v, callback):
        row = tk.Frame(parent, bg=PANEL_BG, pady=2)
        row.pack(fill="x")

        lbl = tk.Label(row, text=label_text, width=20, anchor="w", font=("Segoe UI", 9), fg=TEXT_COLOR, bg=PANEL_BG)
        lbl.pack(side="left")

        val_var = tk.IntVar()
        scale = ttk.Scale(row, from_=min_v, to=max_v, variable=val_var, orient="horizontal", command=callback)
        scale.pack(side="left", fill="x", expand=True, padx=8)

        val_lbl = tk.Label(row, text="--", width=4, font=("Segoe UI", 9, "bold"), fg="#93c5fd", bg=PANEL_BG)
        val_lbl.pack(side="right")

        return val_var, val_lbl

    def _load_live_values(self):
        try:
            b = self.ctl.get_brightness()
            if b is not None:
                self.brightness_var.set(b)
                self.b_val_lbl.config(text=str(b))

            c = self.ctl.get_contrast()
            if c is not None:
                self.contrast_var.set(c)
                self.c_val_lbl.config(text=str(c))

            s = self.ctl.get_sharpness()
            if s is not None:
                self.sharpness_var.set(s)
                self.s_val_lbl.config(text=str(s))

            bl = self.ctl.get_black_level()
            if bl is not None:
                self.black_level_var.set(bl)
                self.bl_val_lbl.config(text=str(bl))

            dcr = self.ctl.get_dcr()
            if dcr is not None:
                self.dcr_var.set(dcr)
                self.dcr_val_lbl.config(text=str(dcr))

            sm = self.ctl.get_smart_mode()
            if sm in SMART_MODES:
                self.smart_mode_combo.set(SMART_MODES[sm])

            cp = self.ctl.get_color_temp_preset()
            if cp in COLOR_PRESETS:
                self.color_preset_combo.set(COLOR_PRESETS[cp])

            r, g, blue = self.ctl.get_rgb_gains()
            if r is not None:
                self.r_var.set(r); self.r_lbl.config(text=str(r))
            if g is not None:
                self.g_var.set(g); self.g_lbl.config(text=str(g))
            if blue is not None:
                self.b_gain_var.set(blue); self.bg_lbl.config(text=str(blue))

            fs = self.ctl.get_freesync()
            if fs:
                self.fs_btn.config(text="ENABLED", bg="#059669")
            else:
                self.fs_btn.config(text="DISABLED", bg="#4b5563")
        except Exception as e:
            print("Error loading values:", e)

    def _on_brightness_change(self, val):
        v = int(float(val))
        self.b_val_lbl.config(text=str(v))
        threading.Thread(target=self.ctl.set_brightness, args=(v,), daemon=True).start()

    def _on_contrast_change(self, val):
        v = int(float(val))
        self.c_val_lbl.config(text=str(v))
        threading.Thread(target=self.ctl.set_contrast, args=(v,), daemon=True).start()

    def _on_sharpness_change(self, val):
        v = int(float(val))
        self.s_val_lbl.config(text=str(v))
        threading.Thread(target=self.ctl.set_sharpness, args=(v,), daemon=True).start()

    def _on_black_level_change(self, val):
        v = int(float(val))
        self.bl_val_lbl.config(text=str(v))
        threading.Thread(target=self.ctl.set_black_level, args=(v,), daemon=True).start()

    def _on_dcr_change(self, val):
        v = int(float(val))
        self.dcr_val_lbl.config(text=str(v))
        threading.Thread(target=self.ctl.set_dcr, args=(v,), daemon=True).start()

    def _on_smartmode_select(self, event):
        sel = self.smart_mode_combo.get()
        for k, v in SMART_MODES.items():
            if v == sel:
                threading.Thread(target=self.ctl.set_smart_mode, args=(k,), daemon=True).start()
                break

    def _on_color_preset_select(self, event):
        sel = self.color_preset_combo.get()
        for k, v in COLOR_PRESETS.items():
            if v == sel:
                threading.Thread(target=self.ctl.set_color_temp_preset, args=(k,), daemon=True).start()
                break

    def _on_rgb_change(self):
        r = self.r_var.get()
        g = self.g_var.get()
        b = self.b_gain_var.get()
        self.r_lbl.config(text=str(r))
        self.g_lbl.config(text=str(g))
        self.bg_lbl.config(text=str(b))
        threading.Thread(target=self.ctl.set_rgb_gains, args=(r, g, b), daemon=True).start()

    def _toggle_freesync(self):
        cur = self.ctl.get_freesync()
        new_state = not cur
        self.ctl.set_freesync(new_state)
        if new_state:
            self.fs_btn.config(text="ENABLED", bg="#059669")
        else:
            self.fs_btn.config(text="DISABLED", bg="#4b5563")

    def _switch_input(self, input_val, label):
        if messagebox.askyesno("Switch Video Input", f"Switch monitor to {label}?\n(Make sure the cable is connected!)"):
            self.ctl.switch_input(input_val)

def main():
    root = tk.Tk()
    app = DisplayCommanderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
