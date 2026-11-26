APP_TO_MODE = {
    "chrome.exe": "cursor",
    "vlc.exe": "media",
    "powerpnt.exe": "presentation",
}
DEFAULT_MODE = "cursor"   # FR-3.5: unsupported app -> normal mouse control


def active_process_name():
    try:
        import win32gui, win32process, psutil
        hwnd = win32gui.GetForegroundWindow()
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        return psutil.Process(pid).name().lower()
    except Exception:
        return None


def mode_for_active_app():
    return APP_TO_MODE.get(active_process_name(), DEFAULT_MODE)
