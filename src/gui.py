import wx
import os
import json
import traceback
import sys
from .config import config
from .translator import translator

class SettingsWindow(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Ajustes del Traductor", size=(450, 550), 
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        # Definir motores tradicionales disponibles
        self.traditional_engines = [
            "google", "bing", "baidu", "alibaba", "tencent", "alibaba", "itranslate", 
            "papago", "reverso", "sogou", "youdao", "modernMt", "deepl", "yandex"
        ]
        
        self.InitUI()
        self.Centre()

    def InitUI(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(245, 247, 250)) # Soft modern background
        vbox = wx.BoxSizer(wx.VERTICAL)

        # Set modern font
        font = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Segoe UI")
        bold_font = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Segoe UI")
        title_font = wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Segoe UI")

        title = wx.StaticText(panel, label="Universal Translator Settings")
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(30, 40, 60))
        vbox.Add(title, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=15)

        # --- Clave API ---
        lbl_key = wx.StaticText(panel, label="Clave API de OpenRouter:")
        vbox.Add(lbl_key, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        self.txt_key = wx.TextCtrl(panel, style=wx.TE_PASSWORD)
        self.txt_key.SetValue(config.API_KEY or "")
        vbox.Add(self.txt_key, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)

        # --- Idiomas ---
        self.langs_display = [
            "Detección automática", "Afrikáans", "Albanés", "Alemán", "Amhárico", "Árabe", "Armenio", "Azerbaiyano",
            "Bengalí", "Bielorruso", "Birmano", "Bosnio", "Búlgaro", "Catalán", "Cebuano", "Checo", "Chichewa",
            "Chino (Simplificado)", "Chino (Tradicional)", "Coreano", "Corso", "Criollo haitiano", "Croata",
            "Danés", "Eslovaco", "Esloveno", "Español", "Esperanto", "Estonio", "Euskera", "Finlandés", "Francés",
            "Frisón", "Gaelico escocés", "Galés", "Gallego", "Georgiano", "Griego", "Gujarati", "Hausa", "Hawaiano",
            "Hebreo", "Hindi", "Hmong", "Húngaro", "Igbo", "Indonesio", "Inglés", "Irlandés", "Islandés", "Italiano",
            "Japonés", "Javanés", "Kannada", "Kazajo", "Jemer", "Kirguís", "Kurdo", "Lao", "Latín", "Letón", "Lituano",
            "Luxemburgués", "Macedonio", "Malayalam", "Malayo", "Malgache", "Maltés", "Maorí", "Maratí", "Mongol",
            "Neerlandés", "Nepalí", "Noruego", "Orija", "Pastún", "Persa", "Polaco", "Portugués", "Punjabi", "Rumano",
            "Ruso", "Samoano", "Serbio", "Sesoto", "Shona", "Sindhi", "Sinhalés", "Somalí", "Sundanés", "Suajili",
            "Sueco", "Tagalo", "Tailandés", "Tamil", "Tártaro", "Tayiko", "Telugu", "Tibetano", "Turco", "Turcomano",
            "Ucraniano", "Urdu", "Uigur", "Uzbeko", "Vietnamita", "Xhosa", "Yidis", "Yoruba", "Zulú"
        ]
        self.langs_map = {lang: lang if lang != "Detección automática" else "auto" for lang in self.langs_display}
        self.reverse_map = {v: k for k, v in self.langs_map.items()}

        # Origen
        lbl_src = wx.StaticText(panel, label="Idioma de origen:")
        vbox.Add(lbl_src, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        self.cb_source = wx.ComboBox(panel, choices=self.langs_display, style=wx.CB_READONLY)
        self.cb_source.SetValue(self.reverse_map.get(config.SOURCE_LANG, "Detección automática"))
        vbox.Add(self.cb_source, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)

        # Destino
        lbl_tgt = wx.StaticText(panel, label="Idioma de destino:")
        vbox.Add(lbl_tgt, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        self.cb_target = wx.ComboBox(panel, choices=self.langs_display[1:], style=wx.CB_READONLY)
        self.cb_target.SetValue(self.reverse_map.get(config.TARGET_LANG, "Español"))
        vbox.Add(self.cb_target, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)

        # --- Modo de Traducción ---
        lbl_mode = wx.StaticText(panel, label="Modo de traducción:")
        vbox.Add(lbl_mode, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        self.cb_mode = wx.ComboBox(panel, choices=["Modo IA", "Modo Tradicional"], style=wx.CB_READONLY)
        self.cb_mode.SetValue("Modo IA" if config.TRANSLATION_MODE == "AI" else "Modo Tradicional")
        self.cb_mode.Bind(wx.EVT_COMBOBOX, self.OnModeChange)
        vbox.Add(self.cb_mode, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)

        # --- Motor / Modelo Dinámico ---
        self.lbl_engine = wx.StaticText(panel, label="Modelo de IA:")
        vbox.Add(self.lbl_engine, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        self.cb_engine = wx.ComboBox(panel, style=wx.CB_READONLY)
        vbox.Add(self.cb_engine, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)
        
        # Cargar opciones iniciales del motor
        self.UpdateEngineOptions()

        # --- Modo Contextual ---
        self.chk_context = wx.CheckBox(panel, label="Activar modo contextual (historial)")
        self.chk_context.SetFont(font)
        self.chk_context.SetValue(getattr(config, 'CONTEXT_MODE', False))
        vbox.Add(self.chk_context, flag=wx.ALL, border=10)

        self.btn_clear = wx.Button(panel, label="Vaciar historial actual")
        self.btn_clear.SetFont(font)
        self.btn_clear.Bind(wx.EVT_BUTTON, self.OnClearHistory)
        vbox.Add(self.btn_clear, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=10)

        # --- Botón Guardar ---
        self.btn_save = wx.Button(panel, label="Guardar cambios", size=(-1, 40))
        self.btn_save.SetFont(bold_font)
        self.btn_save.SetBackgroundColour(wx.Colour(0, 120, 215)) # Windows blue
        self.btn_save.SetForegroundColour(wx.WHITE)
        self.btn_save.SetDefault()
        self.btn_save.Bind(wx.EVT_BUTTON, self.OnSave)
        vbox.Add(self.btn_save, flag=wx.EXPAND|wx.ALL, border=20)

        # Apply basic font to all children
        for child in panel.GetChildren():
            if isinstance(child, wx.StaticText) and child != title:
                child.SetFont(bold_font)
                child.SetForegroundColour(wx.Colour(50, 60, 75))
            elif isinstance(child, (wx.TextCtrl, wx.ComboBox)):
                child.SetFont(font)

        panel.SetSizer(vbox)
        vbox.Fit(self)

    def UpdateEngineOptions(self):
        mode = self.cb_mode.GetValue()
        if mode == "Modo IA":
            self.lbl_engine.SetLabel("Modelo de IA:")
            models = list(config.AVAILABLE_MODELS.keys())
            self.cb_engine.SetItems(models)
            
            # Buscar el nombre del modelo actual
            current_model_name = models[0]
            for name, mid in config.AVAILABLE_MODELS.items():
                if mid == config.MODEL:
                    current_model_name = name
                    break
            self.cb_engine.SetValue(current_model_name)
        else:
            self.lbl_engine.SetLabel("Servidor de traducción:")
            self.cb_engine.SetItems(self.traditional_engines)
            if config.FAST_ENGINE in self.traditional_engines:
                self.cb_engine.SetValue(config.FAST_ENGINE)
            else:
                self.cb_engine.SetValue("google")

    def OnModeChange(self, event):
        self.UpdateEngineOptions()

    def OnClearHistory(self, event):
        translator.clear_history()
        wx.MessageBox("Historial de conversación vaciado.", "Información", wx.OK | wx.ICON_INFORMATION)

    def OnSave(self, event):
        try:
            api_key = self.txt_key.GetValue().strip()
            source = self.langs_map.get(self.cb_source.GetValue(), "auto")
            target = self.langs_map.get(self.cb_target.GetValue(), "Spanish")
            context_mode = self.chk_context.GetValue()
            
            mode_val = self.cb_mode.GetValue()
            translation_mode = "AI" if mode_val == "Modo IA" else "Fast"
            
            model_id = config.MODEL
            fast_engine = config.FAST_ENGINE
            
            if translation_mode == "AI":
                model_id = config.AVAILABLE_MODELS.get(self.cb_engine.GetValue(), config.MODEL)
            else:
                fast_engine = self.cb_engine.GetValue()
            
            # Guardar físicamente
            if config.save(source, target, model_id, api_key, context_mode, translation_mode, fast_engine):
                self.EndModal(wx.ID_OK)
            else:
                wx.MessageBox("Error al guardar.", "Error", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            traceback.print_exc()
            wx.MessageBox(f"Error: {e}", "Error", wx.OK | wx.ICON_ERROR)

def show_first_run_dialog():
    app = wx.GetApp() or wx.App(False)
    dlg = wx.TextEntryDialog(None, "No se ha encontrado una clave API de OpenRouter.\nPor favor, introdúcela para comenzar:", 
                              "Configuración Inicial", 
                              style=wx.OK | wx.CANCEL | wx.CENTRE | wx.TE_PASSWORD)
    res = False
    if dlg.ShowModal() == wx.ID_OK:
        key = dlg.GetValue().strip()
        if key:
            config.save(api_key=key)
            res = True
    dlg.Destroy()
    return res

def show_settings():
    app = wx.GetApp() or wx.App(False)
    # Usar el diálogo de forma modal para que capture el foco y sea accesible
    dlg = SettingsWindow(None)
    dlg.ShowModal()
    dlg.Destroy()
