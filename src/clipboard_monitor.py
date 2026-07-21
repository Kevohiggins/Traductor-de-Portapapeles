import win32clipboard
import time
import threading

class ClipboardMonitor(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.running = True
        self.daemon = True
        # Set to current text to avoid translating old content on startup
        self.last_text = self.get_clipboard_text() or ""

    def get_clipboard_text(self):
        try:
            win32clipboard.OpenClipboard()
        except Exception:
            return None # Acceso denegado o en uso por otra app

        try:
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
            elif win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_TEXT):
                data = win32clipboard.GetClipboardData(win32clipboard.CF_TEXT).decode('utf-8', errors='ignore')
            else:
                data = None
            return data
        except Exception:
            return None
        finally:
            try:
                win32clipboard.CloseClipboard()
            except:
                pass

    def run(self):
        while self.running:
            current_text = self.get_clipboard_text()
            if current_text and current_text != self.last_text:
                self.last_text = current_text
                self.callback(current_text, "Clipboard")
            time.sleep(0.5)

    def stop(self):
        self.running = False

    def set_clipboard_text(self, text):
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            self.last_text = text  # Actualizamos last_text para evitar el bucle infinito
            return True
        except Exception as e:
            print(f"[Clipboard] Error al escribir: {e}")
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
            return False
