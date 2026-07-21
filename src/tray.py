import wx
import wx.adv
import webbrowser
import os
import sys
from .gui import show_settings
from .translator import translator
from .tts import tts

def open_manual():
    print("[Tray] Abriendo manual...", flush=True)
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    manual_path = os.path.join(base_dir, "Manual.html")
    if os.path.exists(manual_path):
        webbrowser.open(f"file://{manual_path}")
    else:
        print("[Tray] Manual.html no encontrado.")

class MyTaskBarIcon(wx.adv.TaskBarIcon):
    def __init__(self, stop_callback):
        super().__init__()
        self.stop_callback = stop_callback
        
        # Crear icono con wx
        icon = self.create_icon()
        self.SetIcon(icon, "Traductor de Portapapeles")
        
        self.Bind(wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.on_settings)

    def create_icon(self):
        # Crear un icono simple 32x32 de color azul con letra blanca
        bmp = wx.Bitmap(32, 32)
        dc = wx.MemoryDC()
        dc.SelectObject(bmp)
        dc.SetBackground(wx.Brush(wx.Colour(0, 120, 215))) # Azul de windows
        dc.Clear()
        dc.SetTextForeground(wx.WHITE)
        font = wx.Font(20, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        dc.SetFont(font)
        dc.DrawText("T", 6, 2)
        dc.SelectObject(wx.NullBitmap)
        
        icon = wx.Icon()
        icon.CopyFromBitmap(bmp)
        return icon

    def CreatePopupMenu(self):
        menu = wx.Menu()
        
        item_help = wx.MenuItem(menu, wx.ID_ANY, "Ayuda (Manual)")
        menu.Append(item_help)
        self.Bind(wx.EVT_MENU, self.on_help, item_help)
        
        item_settings = wx.MenuItem(menu, wx.ID_ANY, "Ajustes")
        menu.Append(item_settings)
        self.Bind(wx.EVT_MENU, self.on_settings, item_settings)
        
        menu.AppendSeparator()
        
        item_quit = wx.MenuItem(menu, wx.ID_ANY, "Salir")
        menu.Append(item_quit)
        self.Bind(wx.EVT_MENU, self.on_quit, item_quit)
        
        return menu

    def on_help(self, event):
        open_manual()

    def on_settings(self, event):
        show_settings()

    def on_quit(self, event):
        print("[Tray] Saliendo del programa...", flush=True)
        self.RemoveIcon()
        self.stop_callback()

def start_tray(stop_callback):
    # Ya no necesita thread separado, corre en el MainLoop de wx
    tray = MyTaskBarIcon(stop_callback)
    return tray
