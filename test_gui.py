import sys
import os
sys.path.append(os.path.dirname(__file__))

import wx
from src.gui import SettingsWindow

app = wx.App(False)
print("Instanciando ventana...")
try:
    dlg = SettingsWindow(None)
    print("Ventana instanciada.")
    dlg.Destroy()
except Exception as e:
    import traceback
    traceback.print_exc()
