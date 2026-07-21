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
        self.MODEL_DIR = os.path.join(self.internal_dir, "models", "nllb-ct2")
        
        # Valores por defecto iniciales
        self.SOURCE_LANG = "Inglés"
        self.TARGET_LANG = "Español"
        self.COPY_TO_CLIPBOARD = True
        self.BEAM_SIZE = 4
        self.SPLIT_SENTENCES = False
        
        self.load()

    def load(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.SOURCE_LANG = data.get("source_lang", self.SOURCE_LANG)
                    self.TARGET_LANG = data.get("target_lang", self.TARGET_LANG)
                    self.COPY_TO_CLIPBOARD = data.get("copy_to_clipboard", self.COPY_TO_CLIPBOARD)
                    self.BEAM_SIZE = data.get("beam_size", self.BEAM_SIZE)
                    self.SPLIT_SENTENCES = data.get("split_sentences", self.SPLIT_SENTENCES)
                print(f"[Config] Cargada configuración desde {self.CONFIG_FILE}", flush=True)
            except Exception as e:
                print(f"[Config] Error al cargar: {e}", flush=True)

    def save(self, source_lang=None, target_lang=None, copy_to_clipboard=None, beam_size=None, split_sentences=None):
        if source_lang: self.SOURCE_LANG = source_lang
        if target_lang: self.TARGET_LANG = target_lang
        if copy_to_clipboard is not None: self.COPY_TO_CLIPBOARD = copy_to_clipboard
        if beam_size is not None: self.BEAM_SIZE = beam_size
        if split_sentences is not None: self.SPLIT_SENTENCES = split_sentences
        
        data = {
            "source_lang": self.SOURCE_LANG,
            "target_lang": self.TARGET_LANG,
            "copy_to_clipboard": self.COPY_TO_CLIPBOARD,
            "beam_size": self.BEAM_SIZE,
            "split_sentences": self.SPLIT_SENTENCES
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
