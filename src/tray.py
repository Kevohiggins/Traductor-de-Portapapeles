import pystray
from PIL import Image, ImageDraw
import threading
import os
import sys
import wx
from .gui import show_settings
from .translator import translator

def create_image():
    # Generar un icono simple (un cuadrado azul con una 'T')
    width = 64
    height = 64
    color1 = "blue"
    color2 = "white"
    image = Image.new('RGB', (width, height), color1)
    dc = ImageDraw.Draw(image)
    dc.text((20, 10), "T", fill=color2, size=40)
    return image

class TrayIcon:
    def __init__(self, stop_callback):
        self.stop_callback = stop_callback
        self.icon = None

    def on_settings(self, icon, item):
        # Usar CallAfter para asegurar que la UI se maneja en el hilo principal de wx
        print("[Tray] Petición de apertura de ajustes...", flush=True)
        wx.CallAfter(show_settings)

    def on_quit(self, icon, item):
        print("[Tray] Saliendo del programa...", flush=True)
        self.icon.stop()
        self.stop_callback()

    def on_clear_history(self, icon, item):
        translator.clear_history()
        from .tts import tts
        tts.speak("Historial vaciado", interrupt=True)

    def run(self):
        self.icon = pystray.Icon("Traductor de Portapapeles", create_image(), "Traductor de Portapapeles", 
                                menu=pystray.Menu(
                                    pystray.MenuItem("Vaciar historial", self.on_clear_history),
                                    pystray.MenuItem("Ajustes", self.on_settings),
                                    pystray.MenuItem("Salir", self.on_quit)
                                ))
        self.icon.run()

def start_tray(stop_callback):
    tray = TrayIcon(stop_callback)
    threading.Thread(target=tray.run, daemon=True).start()
    return tray
