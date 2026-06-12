import time
import sys
import os
import threading
import wx
from .config import config
from .clipboard_monitor import ClipboardMonitor
from .translator import translator
from .tts import tts
from .tray import start_tray
from .hotkey import HotkeyMonitor
from .gui import show_settings, show_first_run_dialog

# Global state to prevent duplicates and handle debouncing
_last_processed_text = ""
_process_lock = threading.Lock()
_debounce_timer = None

def process_text(text, source):
    global _last_processed_text, _debounce_timer
    
    text = text.strip()
    if not text or len(text) < 2: # Evitar ruidos o textos muy cortos
        return

    with _process_lock:
        if text == _last_processed_text:
            return
        _last_processed_text = text

    # Cancelar traducción previa si hay una ráfaga (debouncing de 300ms)
    if _debounce_timer:
        _debounce_timer.cancel()
    
    def delayed_process():
        print(f"[{source}] Procesando: {text[:50]}...", flush=True)
        # Traducir
        translation = translator.translate(text)
        
        if translation and not translation.startswith("Error:"):
            print(f"[{source}] Traducción: {translation}", flush=True)
            # Verbalizar
            tts.speak(translation, interrupt=True)
        elif translation.startswith("Error:"):
            print(f"[{source}] Omitiendo verbalización de error técnico.", flush=True)

    _debounce_timer = threading.Timer(0.3, delayed_process)
    _debounce_timer.start()

def main():
    # Iniciar la aplicación de wx
    app = wx.App(False)
    
    # Cargar configuración inicial
    config.load()
    
    # Crear un frame oculto (top-level window) para que el MainLoop no termine
    hidden_frame = wx.Frame(None, title="Traductor Hidden Helper")
    
    # Mensaje de bienvenida
    tts.speak("Traductor de portapapeles activo.", interrupt=True)

    # Si no hay clave API, pedirla inmediatamente
    if not config.API_KEY:
        print("[Inicio] Clave API no detectada. Abriendo diálogo...", flush=True)
        success = show_first_run_dialog()
        if not success or not config.API_KEY:
            print("[Inicio] No se proporcionó clave API. Saliendo.", flush=True)
            return

    print("Traductor de Portapapeles - Ejecutándose", flush=True)
    
    # Monitores
    clip_monitor = ClipboardMonitor(process_text)
    clip_monitor.start()

    def on_hotkey_settings():
        print("[Hotkey] Abriendo ajustes...", flush=True)
        wx.CallAfter(show_settings)

    def on_hotkey_clear():
        print("[Hotkey] Vaciando historial...", flush=True)
        translator.clear_history()
        tts.speak("Historial vaciado", interrupt=True)
        
    def on_hotkey_exit():
        print("[Hotkey] Cerrando programa...", flush=True)
        tts.speak("Cerrando traductor", interrupt=True)
        stop_all()

    callbacks = {
        1: on_hotkey_settings,
        2: on_hotkey_clear,
        3: on_hotkey_exit
    }
    hotkey_monitor = HotkeyMonitor(callbacks)
    hotkey_monitor.start()

    def stop_all():
        print("\nDeteniendo todo de forma segura...", flush=True)
        clip_monitor.stop()
        hotkey_monitor.stop()
        
        def final_exit():
            try:
                hidden_frame.Close()
                app.ExitMainLoop()
            except:
                pass
            sys.exit(0)
            
        wx.CallAfter(final_exit)

    # Iniciar icono en la bandeja
    start_tray(stop_all)
    
    # El MainLoop ahora se mantendrá vivo gracias al hidden_frame
    app.MainLoop()

if __name__ == "__main__":
    main()
