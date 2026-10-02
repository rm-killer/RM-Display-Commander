import ctypes
from ctypes import wintypes
import time

user32 = ctypes.windll.user32
dxva2 = ctypes.windll.dxva2

class PHYSICAL_MONITOR(ctypes.Structure):
    _fields_ = [
        ("hPhysicalMonitor", wintypes.HANDLE),
        ("szPhysicalMonitorDescription", wintypes.WCHAR * 128)
    ]

# HARD SAFETY: FORBIDDEN OPCODES THAT MUST NEVER BE SENT
FORBIDDEN_VCP_CODES = {
    0xD6: "Power Mode (Firmware bug trigger)",
}

class MonitorController:
    def __init__(self):
        self.h_physical = None
        self.description = ""
        self._init_monitor()

    def _init_monitor(self):
        monitors = []
        def callback(hMonitor, hdcMonitor, lprcMonitor, dwData):
            monitors.append(hMonitor)
            return True
        MONITORENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HMONITOR, wintypes.HDC, ctypes.POINTER(wintypes.RECT), wintypes.LPARAM)
        user32.EnumDisplayMonitors(None, None, MONITORENUMPROC(callback), 0)

        if not monitors:
            raise RuntimeError("No display monitors detected.")

        count = wintypes.DWORD()
        if not dxva2.GetNumberOfPhysicalMonitorsFromHMONITOR(monitors[0], ctypes.byref(count)):
            raise RuntimeError("Failed to query physical monitors.")

        phy_array = (PHYSICAL_MONITOR * count.value)()
        if not dxva2.GetPhysicalMonitorsFromHMONITOR(monitors[0], count.value, phy_array):
            raise RuntimeError("Failed to get physical monitor handles.")

        self.h_physical = phy_array[0].hPhysicalMonitor
        self.description = str(phy_array[0].szPhysicalMonitorDescription)

    def close(self):
        if self.h_physical:
            dxva2.DestroyPhysicalMonitor(self.h_physical)
            self.h_physical = None

    def get_vcp(self, code: int):
        """Reads (current_value, max_value, vcp_type) from monitor."""
        if not self.h_physical:
            self._init_monitor()
        pvct, cur, max_v = wintypes.DWORD(), wintypes.DWORD(), wintypes.DWORD()
        res = dxva2.GetVCPFeatureAndVCPFeatureReply(self.h_physical, code, ctypes.byref(pvct), ctypes.byref(cur), ctypes.byref(max_v))
        if res:
            return cur.value, max_v.value, pvct.value
        return None

    def set_vcp(self, code: int, value: int):
        """Safely writes a VCP feature, blocking forbidden dangerous opcodes."""
        if code in FORBIDDEN_VCP_CODES:
            raise PermissionError(f"BLOCKED: VCP {hex(code)} ({FORBIDDEN_VCP_CODES[code]}) is permanently disabled for hardware safety.")
        if not self.h_physical:
            self._init_monitor()
        res = dxva2.SetVCPFeature(self.h_physical, code, value)
        return bool(res)

    # Convenience API helpers
    def get_brightness(self):
        r = self.get_vcp(0x10)
        return r[0] if r else None

    def set_brightness(self, val: int):
        return self.set_vcp(0x10, max(0, min(100, val)))

    def get_contrast(self):
        r = self.get_vcp(0x12)
        return r[0] if r else None

    def set_contrast(self, val: int):
        return self.set_vcp(0x12, max(0, min(100, val)))

    def get_sharpness(self):
        r = self.get_vcp(0x0E)
        return r[0] if r else None

    def set_sharpness(self, val: int):
        return self.set_vcp(0x0E, max(0, min(100, val)))

    def get_black_level(self):
        r = self.get_vcp(0x6C)
        return r[0] if r else None

    def set_black_level(self, val: int):
        return self.set_vcp(0x6C, max(0, min(255, val)))

    def get_dcr(self):
        r = self.get_vcp(0x6E)
        return r[0] if r else None

    def set_dcr(self, val: int):
        return self.set_vcp(0x6E, max(0, min(255, val)))

    def get_smart_mode(self):
        r = self.get_vcp(0xDC)
        return r[0] if r else None

    def set_smart_mode(self, mode: int):
        return self.set_vcp(0xDC, mode)

    def get_freesync(self):
        r = self.get_vcp(0xED)
        return bool(r[0]) if r else None

    def set_freesync(self, enabled: bool):
        return self.set_vcp(0xED, 1 if enabled else 0)

    def get_color_temp_preset(self):
        r = self.get_vcp(0x14)
        return r[0] if r else None

    def set_color_temp_preset(self, preset: int):
        return self.set_vcp(0x14, preset)

    def get_rgb_gains(self):
        r = self.get_vcp(0x16)
        g = self.get_vcp(0x18)
        b = self.get_vcp(0x1A)
        return (r[0] if r else None, g[0] if g else None, b[0] if b else None)

    def set_rgb_gains(self, r: int, g: int, b: int):
        ok_r = self.set_vcp(0x16, max(0, min(100, r)))
        ok_g = self.set_vcp(0x18, max(0, min(100, g)))
        ok_b = self.set_vcp(0x1A, max(0, min(100, b)))
        return ok_r and ok_g and ok_b

    def switch_input(self, input_val: int):
        return self.set_vcp(0x60, input_val)
