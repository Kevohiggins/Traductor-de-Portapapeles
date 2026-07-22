import os
import json
import sys
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
            self.internal_dir = sys._MEIPASS
        else:
            self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            self.internal_dir = self.base_dir
            
        self.CONFIG_FILE = os.path.join(self.base_dir, "config.json")
        self.MODEL_DIR = os.path.join(self.internal_dir, "models", "gemma-2b-ct2")
        
        # Valores por defecto iniciales
        self.SOURCE_LANG = "Inglés"
        self.TARGET_LANG = "Español"
        self.COPY_TO_CLIPBOARD = True
        self.USE_CONTEXT = False
        
        self.load()

    def load(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.SOURCE_LANG = data.get("source_lang", self.SOURCE_LANG)
                    self.TARGET_LANG = data.get("target_lang", self.TARGET_LANG)
                    self.COPY_TO_CLIPBOARD = data.get("copy_to_clipboard", self.COPY_TO_CLIPBOARD)
                    self.USE_CONTEXT = data.get("use_context", self.USE_CONTEXT)
                print(f"[Config] Cargada configuración desde {self.CONFIG_FILE}", flush=True)
            except Exception as e:
                print(f"[Config] Error al cargar: {e}", flush=True)

    def save(self, source_lang=None, target_lang=None, copy_to_clipboard=None, use_context=None):
        if source_lang: self.SOURCE_LANG = source_lang
        if target_lang: self.TARGET_LANG = target_lang
        if copy_to_clipboard is not None: self.COPY_TO_CLIPBOARD = copy_to_clipboard
        if use_context is not None: self.USE_CONTEXT = use_context
        
        data = {
            "source_lang": self.SOURCE_LANG,
            "target_lang": self.TARGET_LANG,
            "copy_to_clipboard": self.COPY_TO_CLIPBOARD,
            "use_context": self.USE_CONTEXT
        }
        
        try:
            with open(self.CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
            print(f"[Config] Guardada configuración en {self.CONFIG_FILE}", flush=True)
            return True
        except Exception as e:
            print(f"[Config] Error al guardar: {e}", flush=True)
            return False

config = Config()
