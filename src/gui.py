import wx
import traceback
from .config import config
from .languages import NLLB_LANGUAGES

class SettingsWindow(wx.Dialog):
    def __init__(self, parent):
        super().__init__(parent, title="Ajustes del Traductor (V3 Gemma)", size=(450, 450), 
                         style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)
        
        self.InitUI()
        self.Centre()

    def InitUI(self):
        panel = wx.Panel(self)
        panel.SetBackgroundColour(wx.Colour(245, 247, 250))
        vbox = wx.BoxSizer(wx.VERTICAL)

        font = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL, False, "Segoe UI")
        bold_font = wx.Font(10, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Segoe UI")
        title_font = wx.Font(14, wx.FONTFAMILY_SWISS, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD, False, "Segoe UI")

        title = wx.StaticText(panel, label="Configuración de Idiomas")
        title.SetFont(title_font)
        title.SetForegroundColour(wx.Colour(30, 40, 60))
        vbox.Add(title, flag=wx.ALIGN_CENTER|wx.TOP|wx.BOTTOM, border=15)

        # Listas de idiomas
        self.source_choices = list(NLLB_LANGUAGES.keys())
        self.target_choices = list(NLLB_LANGUAGES.keys())

        # Origen
        lbl_src = wx.StaticText(panel, label="Idioma de origen:")
        lbl_src.SetFont(bold_font)
        vbox.Add(lbl_src, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=15)
        self.cb_source = wx.ComboBox(panel, choices=self.source_choices, style=wx.CB_READONLY)
        self.cb_source.SetFont(font)
        self.cb_source.SetValue(self._get_source_display_name(config.SOURCE_LANG))
        vbox.Add(self.cb_source, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=15)

        # Botón Intercambiar
        self.btn_swap = wx.Button(panel, label="↑↓ Intercambiar Idiomas")
        self.btn_swap.SetFont(font)
        self.btn_swap.Bind(wx.EVT_BUTTON, self.OnSwapLanguages)
        vbox.Add(self.btn_swap, flag=wx.ALIGN_CENTER|wx.BOTTOM, border=10)

        # Destino
        lbl_tgt = wx.StaticText(panel, label="Idioma de destino:")
        lbl_tgt.SetFont(bold_font)
        vbox.Add(lbl_tgt, flag=wx.LEFT|wx.RIGHT|wx.TOP, border=10)
        self.cb_target = wx.ComboBox(panel, choices=self.target_choices, style=wx.CB_READONLY)
        self.cb_target.SetFont(font)
        self.cb_target.SetValue(self._get_target_display_name(config.TARGET_LANG))
        vbox.Add(self.cb_target, flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM, border=15)

        self.chk_clipboard = wx.CheckBox(panel, label="Copiar traducción al portapapeles")
        self.chk_clipboard.SetFont(font)
        self.chk_clipboard.SetValue(config.COPY_TO_CLIPBOARD)
        vbox.Add(self.chk_clipboard, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=15)

        # Checkbox Contexto Histórico
        self.chk_context = wx.CheckBox(panel, label="Usar Contexto Histórico (Recuerda las últimas 10 traducciones)")
        self.chk_context.SetFont(font)
        self.chk_context.SetValue(config.USE_CONTEXT)
        vbox.Add(self.chk_context, flag=wx.LEFT|wx.RIGHT|wx.BOTTOM, border=15)

        # Botón Guardar
        self.btn_save = wx.Button(panel, label="Guardar cambios", size=(-1, 40))
        self.btn_save.SetFont(bold_font)
        self.btn_save.SetBackgroundColour(wx.Colour(0, 120, 215)) # Azul
        self.btn_save.SetForegroundColour(wx.WHITE)
        self.btn_save.SetDefault()
        self.btn_save.Bind(wx.EVT_BUTTON, self.OnSave)
        vbox.Add(self.btn_save, flag=wx.EXPAND|wx.ALL, border=20)

        panel.SetSizer(vbox)
        vbox.Fit(self)

    def _get_source_display_name(self, internal_name):
        if not internal_name: return self.source_choices[0]
        # Buscar el nombre por defecto guardado en config
        for name in self.source_choices:
            if name == internal_name:
                return name
        return self.source_choices[0]
        
    def _get_target_display_name(self, internal_name):
        if not internal_name: return "Español"
        for name in self.target_choices:
            if name == internal_name:
                return name
        return "Español"

    def OnSwapLanguages(self, event):
        src = self.cb_source.GetValue()
        tgt = self.cb_target.GetValue()
        self.cb_source.SetValue(tgt)
        self.cb_target.SetValue(src)

    def OnSave(self, event):
        try:
            source = self.cb_source.GetValue()
            target = self.cb_target.GetValue()
            copy_cb = self.chk_clipboard.GetValue()
            context_cb = self.chk_context.GetValue()
            
            if config.save(source_lang=source, target_lang=target, copy_to_clipboard=copy_cb, use_context=context_cb):
                self.EndModal(wx.ID_OK)
            else:
                wx.MessageBox("Error al guardar la configuración.", "Error", wx.OK | wx.ICON_ERROR)
        except Exception as e:
            import traceback
            traceback.print_exc()
            wx.MessageBox(f"Error: {e}", "Error", wx.OK | wx.ICON_ERROR)

def show_first_run_dialog():
    return True

def show_settings():
    app = wx.GetApp() or wx.App(False)
    dlg = SettingsWindow(None)
    # Forzar la ventana al frente (a veces Windows la oculta por no tener ventana principal)
    dlg.SetWindowStyle(dlg.GetWindowStyle() | wx.STAY_ON_TOP)
    dlg.Raise()
    dlg.ShowModal()
    dlg.Destroy()
