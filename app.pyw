import threading
import time
import ctypes
import webview
from api import app as flask_app

def start_flask():
    flask_app.run(port=5000, debug=False, use_reloader=False)

def set_square_corners():
    time.sleep(0.5)
    hwnd = ctypes.windll.user32.FindWindowW(None, 'ReadVault')
    if hwnd:
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWMWCP_DONOTROUND = 1
        ctypes.windll.dwmapi.DwmSetWindowAttribute(
            hwnd,
            DWMWA_WINDOW_CORNER_PREFERENCE,
            ctypes.byref(ctypes.c_int(DWMWCP_DONOTROUND)),
            ctypes.sizeof(ctypes.c_int)
        )

if __name__ == '__main__':
    threading.Thread(target=start_flask, daemon=True).start()
    time.sleep(1)

    window = webview.create_window(
        title='ReadVault',
        url='http://localhost:5000',
        width=1400,
        height=860,
        min_size=(900, 600)
    )
    threading.Thread(target=set_square_corners, daemon=True).start()
    webview.start()
