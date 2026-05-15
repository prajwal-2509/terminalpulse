from __future__ import annotations
import time
import json
import urllib.request
import ctypes
import ctypes.wintypes

PULSE_PORT = 7077
POLL_INTERVAL = 3
EDITORS = {"Visual Studio Code", "Cursor", "VSCodium"}

def get_active_window_title() -> str:
    hwnd = ctypes.windll.user32.GetForegroundWindow()
    length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
    buf = ctypes.create_unicode_buffer(length + 1)
    ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
    return buf.value

IGNORE = {"Visual Studio Code", "Cursor", "Welcome", "New Tab", "Settings", ""}

def extract_file(title: str) -> str | None:
    for editor in EDITORS:
        if editor in title:
            parts = title.split(" - ")
            if parts:
                name = parts[0].strip().lstrip("●").strip()
                if name and name not in IGNORE:
                    return name
    return None
def send_focus(filename: str, port: int = PULSE_PORT):
    payload = json.dumps({
        "type": "focus_changed",
        "path": filename,
        "cwd": ""
    }).encode()
    try:
        req = urllib.request.Request(
            f"http://localhost:{port}",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req, timeout=2)
    except Exception:
        pass

def run():
    print(f"👁  TerminalPulse Windows tracker running (port {PULSE_PORT})")
    last = None
    while True:
        title = get_active_window_title()
        f = extract_file(title)
        if f and f != last:
            print(f"👀 Focus: {f}")
            send_focus(f)
            last = f
        time.sleep(POLL_INTERVAL)

if __name__ == "__main__":
    run()
