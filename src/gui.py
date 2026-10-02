import customtkinter as ctk
import threading
from monitor_api import MonitorController

# Appearance & Global Settings
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

# Design Tokens (UI/UX Pro Max Gaming Hardware Aesthetic)
BG_MAIN = "#0d1117"
CARD_BG = "#161b22"
CARD_BORDER = "#30363d"
ACCENT_BLUE = "#38bdf8"
ACCENT_CYAN = "#06b6d4"
ACCENT_GREEN = "#10b981"
TEXT_PRIMARY = "#f0f6fc"
TEXT_SECONDARY = "#8b949e"

SMART_MODES = {
    0x00: "Standard",
    0x01: "ECO",
    0x02: "Movie",
    0x03: "Game / FPS",
    0x04: "RTS",
    0x05: "Reader / Low Blue Light"
}

COLOR_PRESETS = {
    0x05: "Standard (Neutral)",
    0x08: "Warm",
    0x0B: "Cool",
    0x0C: "Custom RGB"
}

ASPECT_RATIOS = {
    0: "Auto / Full Screen",
    1: "16:9 Standard",
    2: "21:9 Ultrawide"
}

INPUT_SOURCES = [
    ("DisplayPort 1", 0x0F),
    ("DisplayPort 2", 0x10),
    ("HDMI 1", 0x11),
    ("HDMI 2", 0x12)
]

class ModernDisplayCommanderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("RM Display Commander — Xiaomi 34\" Control Hub")
        self.geometry("620x860")
        self.minsize(580, 800)
        self.configure(fg_color=BG_MAIN)

        self.ctl = MonitorController()

        self._build_header()
        self._build_content()
        self._load_live_values()

    def _build_header(self):
        hdr_frame = ctk.CTkFrame(self, fg_color="transparent")
        hdr_frame.pack(fill="x", padx=20, pady=(16, 10))

        title_lbl = ctk.CTkLabel(
            hdr_frame,
            text="RM DISPLAY COMMANDER",
            font=ctk.CTkFont(family="Segoe UI", size=20, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            hdr_frame,
            text=f"Hardware: {self.ctl.description}  |  Xiaomi Mi Curved 34\" (MStar MST9U)",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_SECONDARY
        )
        sub_lbl.pack(anchor="w", pady=(2, 8))

        # Hardware Shield Banner
        shield_frame = ctk.CTkFrame(
            hdr_frame,
            fg_color="#064e3b",
            border_color="#059669",
            border_width=1,
            corner_radius=6
        )
        shield_frame.pack(fill="x")

        shield_lbl = ctk.CTkLabel(
            shield_frame,
            text="🛡️ HARDWARE PROTECTION ACTIVE: VCP 0xD6 PERMANENTLY BLOCKED",
            font=ctk.CTkFont(family="Segoe UI", size=10, weight="bold"),
            text_color="#6ee7b7",
            padx=10,
            pady=4
        )
        shield_lbl.pack(anchor="w")

    def _build_content(self):
        # Scrollable container for perfect sizing
        self.scroll_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#21262d",
            scrollbar_button_hover_color="#30363d"
        )
        self.scroll_frame.pack(fill="both", expand=True, padx=16, pady=4)

        # Panel 1: Image & Luminance
        p1 = self._create_card(self.scroll_frame, "IMAGE & LUMINANCE")
        self.b_slider, self.b_val_lbl = self._create_slider(p1, "Brightness", 0, 100, self._on_brightness)
        self.c_slider, self.c_val_lbl = self._create_slider(p1, "Contrast", 0, 100, self._on_contrast)
        self.s_slider, self.s_val_lbl = self._create_slider(p1, "Sharpness", 0, 100, self._on_sharpness)
        self.bl_slider, self.bl_val_lbl = self._create_slider(p1, "Black Equalizer", 0, 100, self._on_black_level)
        self.sat_slider, self.sat_val_lbl = self._create_slider(p1, "Color Saturation", 0, 100, self._on_saturation)

        # Panel 2: Gaming & Color Modes
        p2 = self._create_card(self.scroll_frame, "GAMING & SMARTMODES")
        self.smart_mode_combo = self._create_dropdown(p2, "SmartMode Preset", list(SMART_MODES.values()), self._on_smartmode)
        self.color_preset_combo = self._create_dropdown(p2, "Color Temperature", list(COLOR_PRESETS.values()), self._on_color_preset)
        self.aspect_ratio_combo = self._create_dropdown(p2, "Aspect Ratio Scaling", list(ASPECT_RATIOS.values()), self._on_aspect_ratio)

        # RGB Gains Section
        rgb_lbl = ctk.CTkLabel(
            p2,
            text="RGB Channel Tuning:",
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=TEXT_SECONDARY
        )
        rgb_lbl.pack(anchor="w", padx=14, pady=(8, 2))

        self.r_slider, self.r_val_lbl = self._create_slider(p2, "Red Gain", 0, 100, lambda v: self._on_rgb(), color="#ef4444")
        self.g_slider, self.g_val_lbl = self._create_slider(p2, "Green Gain", 0, 100, lambda v: self._on_rgb(), color="#10b981")
        self.b_gain_slider, self.bg_val_lbl = self._create_slider(p2, "Blue Gain", 0, 100, lambda v: self._on_rgb(), color="#3b82f6")

        # Panel 3: 1-Click Video Input Switcher
        p3 = self._create_card(self.scroll_frame, "VIDEO INPUT SWITCHER")
        btn_grid = ctk.CTkFrame(p3, fg_color="transparent")
        btn_grid.pack(fill="x", padx=10, pady=8)

        for label, val in INPUT_SOURCES:
            b = ctk.CTkButton(
                btn_grid,
                text=label,
                font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
                fg_color="#21262d",
                hover_color="#30363d",
                text_color=TEXT_PRIMARY,
                height=38,
                corner_radius=6,
                command=lambda v=val, l=label: self._switch_input(v, l)
            )
            b.pack(side="left", fill="x", expand=True, padx=4)

    def _create_card(self, parent, title):
        card = ctk.CTkFrame(
            parent,
            fg_color=CARD_BG,
            border_color=CARD_BORDER,
            border_width=1,
            corner_radius=10
        )
        card.pack(fill="x", pady=8)

        hdr = ctk.CTkLabel(
            card,
            text=title,
            font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"),
            text_color=ACCENT_BLUE
        )
        hdr.pack(anchor="w", padx=14, pady=(12, 6))
        return card

    def _create_slider(self, parent, label_text, min_v, max_v, callback, color=ACCENT_CYAN):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=5)

        lbl = ctk.CTkLabel(
            row,
            text=label_text,
            width=140,
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_PRIMARY
        )
        lbl.pack(side="left")

        slider = ctk.CTkSlider(
            row,
            from_=min_v,
            to=max_v,
            command=callback,
            progress_color=color,
            button_color="#ffffff",
            button_hover_color=color,
            height=16
        )
        slider.pack(side="left", fill="x", expand=True, padx=10)

        val_lbl = ctk.CTkLabel(
            row,
            text="--",
            width=36,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color=ACCENT_BLUE
        )
        val_lbl.pack(side="right")
        return slider, val_lbl

    def _create_dropdown(self, parent, label_text, values, callback):
        row = ctk.CTkFrame(parent, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=6)

        lbl = ctk.CTkLabel(
            row,
            text=label_text,
            width=160,
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=11),
            text_color=TEXT_PRIMARY
        )
        lbl.pack(side="left")

        combo = ctk.CTkOptionMenu(
            row,
            values=values,
            command=callback,
            fg_color="#21262d",
            button_color="#30363d",
            button_hover_color="#484f58",
            dropdown_fg_color="#161b22",
            dropdown_hover_color="#21262d",
            dropdown_text_color=TEXT_PRIMARY,
            text_color=TEXT_PRIMARY,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            dropdown_font=ctk.CTkFont(family="Segoe UI", size=11),
            width=220,
            height=32,
            corner_radius=6
        )
        combo.pack(side="right")
        return combo

    def _load_live_values(self):
        try:
            b = self.ctl.get_brightness()
            if b is not None:
                self.b_slider.set(b); self.b_val_lbl.configure(text=str(b))

            c = self.ctl.get_contrast()
            if c is not None:
                self.c_slider.set(c); self.c_val_lbl.configure(text=str(c))

            s = self.ctl.get_sharpness()
            if s is not None:
                self.s_slider.set(s); self.s_val_lbl.configure(text=str(s))

            bl = self.ctl.get_black_level()
            if bl is not None:
                self.bl_slider.set(bl); self.bl_val_lbl.configure(text=str(bl))

            sat = self.ctl.get_vcp(0x70)
            if sat is not None:
                self.sat_slider.set(sat[0]); self.sat_val_lbl.configure(text=str(sat[0]))

            ar = self.ctl.get_vcp(0x68)
            if ar and ar[0] in ASPECT_RATIOS:
                self.aspect_ratio_combo.set(ASPECT_RATIOS[ar[0]])

            sm = self.ctl.get_smart_mode()
            if sm in SMART_MODES:
                self.smart_mode_combo.set(SMART_MODES[sm])

            cp = self.ctl.get_color_temp_preset()
            if cp in COLOR_PRESETS:
                self.color_preset_combo.set(COLOR_PRESETS[cp])

            r, g, blue = self.ctl.get_rgb_gains()
            if r is not None:
                self.r_slider.set(r); self.r_val_lbl.configure(text=str(r))
            if g is not None:
                self.g_slider.set(g); self.g_val_lbl.configure(text=str(g))
            if blue is not None:
                self.b_gain_slider.set(blue); self.bg_val_lbl.configure(text=str(blue))
        except Exception as e:
            print("Error loading values:", e)

    def _on_brightness(self, val):
        v = int(val)
        self.b_val_lbl.configure(text=str(v))
        threading.Thread(target=self.ctl.set_brightness, args=(v,), daemon=True).start()

    def _on_contrast(self, val):
        v = int(val)
        self.c_val_lbl.configure(text=str(v))
        threading.Thread(target=self.ctl.set_contrast, args=(v,), daemon=True).start()

    def _on_sharpness(self, val):
        v = int(val)
        self.s_val_lbl.configure(text=str(v))
        threading.Thread(target=self.ctl.set_sharpness, args=(v,), daemon=True).start()

    def _on_black_level(self, val):
        v = int(val)
        self.bl_val_lbl.configure(text=str(v))
        threading.Thread(target=self.ctl.set_black_level, args=(v,), daemon=True).start()

    def _on_saturation(self, val):
        v = int(val)
        self.sat_val_lbl.configure(text=str(v))
        threading.Thread(target=self.ctl.set_vcp, args=(0x70, v), daemon=True).start()

    def _on_aspect_ratio(self, val):
        for k, v in ASPECT_RATIOS.items():
            if v == val:
                threading.Thread(target=self.ctl.set_vcp, args=(0x68, k), daemon=True).start()
                break

    def _on_color_preset(self, val):
        for k, v in COLOR_PRESETS.items():
            if v == val:
                threading.Thread(target=self.ctl.set_color_temp_preset, args=(k,), daemon=True).start()
                break

    def _on_rgb(self):
        r = int(self.r_slider.get())
        g = int(self.g_slider.get())
        b = int(self.b_gain_slider.get())
        self.r_val_lbl.configure(text=str(r))
        self.g_val_lbl.configure(text=str(g))
        self.bg_val_lbl.configure(text=str(b))
        threading.Thread(target=self.ctl.set_rgb_gains, args=(r, g, b), daemon=True).start()

    def _on_smartmode(self, val):
        if val == "Standard":
            self._apply_standard()
        elif val == "ECO":
            self._apply_eco()
        elif val == "RTS":
            self._apply_rts()
        elif val == "Game / FPS":
            self._apply_game()
        elif val == "Movie":
            self._apply_movie()
        elif val == "Reader / Low Blue Light":
            self._apply_low_blue()

    def _apply_standard(self):
        threading.Thread(target=self._run_standard, daemon=True).start()
        self.b_slider.set(70); self.b_val_lbl.configure(text="70")
        self.c_slider.set(75); self.c_val_lbl.configure(text="75")
        self.s_slider.set(50); self.s_val_lbl.configure(text="50")
        self.bl_slider.set(50); self.bl_val_lbl.configure(text="50")

    def _run_standard(self):
        self.ctl.set_brightness(70)
        self.ctl.set_contrast(75)
        self.ctl.set_sharpness(50)
        self.ctl.set_black_level(50)
        self.ctl.set_smart_mode(0)

    def _apply_eco(self):
        threading.Thread(target=self._run_eco, daemon=True).start()
        self.b_slider.set(40); self.b_val_lbl.configure(text="40")
        self.c_slider.set(75); self.c_val_lbl.configure(text="75")

    def _run_eco(self):
        self.ctl.set_brightness(40)
        self.ctl.set_contrast(75)

    def _apply_rts(self):
        threading.Thread(target=self._run_rts, daemon=True).start()
        self.b_slider.set(85); self.b_val_lbl.configure(text="85")
        self.c_slider.set(80); self.c_val_lbl.configure(text="80")

    def _run_rts(self):
        self.ctl.set_brightness(85)
        self.ctl.set_contrast(80)

    def _apply_game(self):
        threading.Thread(target=self._run_game, daemon=True).start()
        self.b_slider.set(100); self.b_val_lbl.configure(text="100")
        self.c_slider.set(75); self.c_val_lbl.configure(text="75")

    def _run_game(self):
        self.ctl.set_brightness(100)
        self.ctl.set_contrast(75)
        self.ctl.set_smart_mode(5)

    def _apply_movie(self):
        threading.Thread(target=self._run_movie, daemon=True).start()
        self.b_slider.set(100); self.b_val_lbl.configure(text="100")
        self.c_slider.set(80); self.c_val_lbl.configure(text="80")

    def _run_movie(self):
        self.ctl.set_brightness(100)
        self.ctl.set_contrast(80)
        self.ctl.set_smart_mode(3)

    def _apply_low_blue(self):
        threading.Thread(target=self._run_low_blue, daemon=True).start()
        self.b_slider.set(60); self.b_val_lbl.configure(text="60")
        self.c_slider.set(80); self.c_val_lbl.configure(text="80")

    def _run_low_blue(self):
        self.ctl.set_brightness(60)
        self.ctl.set_contrast(80)

    def _switch_input(self, val, label):
        self.ctl.switch_input(val)

def main():
    app = ModernDisplayCommanderApp()
    app.mainloop()

if __name__ == "__main__":
    main()
