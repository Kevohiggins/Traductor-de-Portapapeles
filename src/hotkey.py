import win32gui
import win32con
import win32api
import threading
import ctypes
from ctypes import wintypes

# RegisterHotKey constants
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
HOTKEY_ID_SETTINGS = 1
HOTKEY_ID_EXIT = 3
HOTKEY_ID_SWAP = 4
HOTKEY_ID_PAUSE = 5
HOTKEY_ID_HELP = 6

class HotkeyMonitor(threading.Thread):
    def __init__(self, callbacks):
        super().__init__()
        self.callbacks = callbacks
        self.running = True
        self.daemon = True

    def run(self):
        # We need a message loop to receive hotkey events
        # Register Ctrl+Shift+C (0x43 is 'C')
        ctypes.windll.user32.RegisterHotKey(None, HOTKEY_ID_SETTINGS, MOD_CONTROL | MOD_SHIFT, 0x43)
        # Register Ctrl+Shift+F4 (0x73 is VK_F4)
        ctypes.windll.user32.RegisterHotKey(None, HOTKEY_ID_EXIT, MOD_CONTROL | MOD_SHIFT, 0x73)
        # Register Ctrl+Shift+S (0x53 is 'S')
        ctypes.windll.user32.RegisterHotKey(None, HOTKEY_ID_SWAP, MOD_CONTROL | MOD_SHIFT, 0x53)
        # Register Ctrl+Shift+P (0x50 is 'P') for pause/resume
        ctypes.windll.user32.RegisterHotKey(None, HOTKEY_ID_PAUSE, MOD_CONTROL | MOD_SHIFT, 0x50)
        # Register Ctrl+Shift+F1 (0x70 is VK_F1) for help
        ctypes.windll.user32.RegisterHotKey(None, HOTKEY_ID_HELP, MOD_CONTROL | MOD_SHIFT, 0x70)

        print("[Hotkey] Teclas registradas correctamente.", flush=True)
        
        try:
            msg = wintypes.MSG()
            while self.running:
                bRet = ctypes.windll.user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if bRet == 0 or bRet == -1:
                    break
                
                if msg.message == win32con.WM_HOTKEY:
                    hotkey_id = msg.wParam
                    if hotkey_id in self.callbacks:
                        self.callbacks[hotkey_id]()
                ctypes.windll.user32.TranslateMessage(ctypes.byref(msg))
                ctypes.windll.user32.DispatchMessageW(ctypes.byref(msg))
        finally:
            ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID_SETTINGS)
            ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID_EXIT)
            ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID_SWAP)
            ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID_PAUSE)
            ctypes.windll.user32.UnregisterHotKey(None, HOTKEY_ID_HELP)

    def stop(self):
        self.running = False
        # Send a dummy message to break GetMessage loop
        ctypes.windll.user32.PostQuitMessage(0)
