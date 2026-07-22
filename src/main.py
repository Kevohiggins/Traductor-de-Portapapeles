import time
import sys
import os
import threading
import wx
from .config import config
from .clipboard_monitor import ClipboardMonitor
from .translator import translator
from .tts import tts
from .tray import start_tray, open_manual
from .hotkey import HotkeyMonitor
from .gui import show_settings, show_first_run_dialog

# Global state to prevent duplicates and handle debouncing
_last_processed_text = ""
_process_lock = threading.Lock()
_debounce_timer = None
clip_monitor = None
is_paused = False


def process_text(text, source):
    global _last_processed_text, _debounce_timer, clip_monitor, is_paused
    
    if is_paused:
        return
        
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
        # Traducir midiendo el tiempo
        import time
        start_time = time.time()
        translation = translator.translate(text)
        elapsed = time.time() - start_time
        
        if translation and not translation.startswith("Error:"):
            print(f"[{source}] Traducción lista en {elapsed:.2f}s", flush=True)
            print(f"[{source}] Resultado: {translation}", flush=True)
            
            # Copiar traducción al portapapeles sin crear bucle infinito
            if clip_monitor and getattr(config, 'COPY_TO_CLIPBOARD', True):
                clip_monitor.set_clipboard_text(translation)
                _last_processed_text = translation
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
    tts.speak("Traductor activado.", interrupt=True)

    # V2 es completamente offline, no se requiere API Key

    print("Traductor de Portapapeles - Ejecutándose", flush=True)
    
    # Monitores
    global clip_monitor
    clip_monitor = ClipboardMonitor(process_text)
    clip_monitor.start()

    def on_hotkey_settings():
        print("[Hotkey] Abriendo ajustes...", flush=True)
        wx.CallAfter(show_settings)
        
    def on_hotkey_exit():
        print("[Hotkey] Cerrando programa...", flush=True)
        tts.speak("Cerrando traductor", interrupt=True)
        stop_all()

    def on_hotkey_swap():
        print(f"[Hotkey] Intercambiando idiomas: {config.SOURCE_LANG} <-> {config.TARGET_LANG}", flush=True)
        old_src = config.SOURCE_LANG
        config.save(source_lang=config.TARGET_LANG, target_lang=old_src)
        tts.speak(f"Destino {config.TARGET_LANG}", interrupt=True)

    def on_hotkey_pause():
        global is_paused
        is_paused = not is_paused
        estado = "pausado" if is_paused else "reanudado"
        print(f"[Hotkey] Traductor {estado}.", flush=True)
        tts.speak(f"Traductor {estado}", interrupt=True)
        
    def on_hotkey_help():
        print("[Hotkey] Abriendo ayuda...", flush=True)
        open_manual()

    callbacks = {
        1: on_hotkey_settings,
        3: on_hotkey_exit,
        4: on_hotkey_swap,
        5: on_hotkey_pause,
        6: on_hotkey_help
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
    global app_tray
    app_tray = start_tray(stop_all)
    
    # El MainLoop ahora se mantendrá vivo gracias al hidden_frame
    app.MainLoop()

if __name__ == "__main__":
    main()
