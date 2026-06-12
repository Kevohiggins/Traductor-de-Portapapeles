import os
import json
import sys
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        # Determinar directorio base de forma robusta
        if getattr(sys, 'frozen', False):
            self.base_dir = os.path.dirname(sys.executable)
        else:
            # En modo script, src/ está dentro del proyecto
            self.base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            
        self.CONFIG_FILE = os.path.join(self.base_dir, "config.json")
        
        self.AVAILABLE_MODELS = {
            "OpenAI GPT-OSS 120B": "openai/gpt-oss-120b:free",
            "NVIDIA Nemotron 3 Ultra 550B": "nvidia/nemotron-3-ultra-550b-a55b:free",
            "NVIDIA Nemotron 3 Super 120B": "nvidia/nemotron-3-super-120b-a12b:free",
            "Google Gemma 4 31B": "google/gemma-4-31b-it",
            "Qwen 3 30B": "qwen/qwen3-30b-a3b-instruct-2507",
            "Mistral NeMo": "mistralai/mistral-nemo",
            "Nex AGI N2 Pro": "nex-agi/nex-n2-pro:free",
            "Llama 4 Scout": "meta-llama/llama-4-scout",
            "Llama 3.1 8B": "meta-llama/llama-3.1-8b-instruct",
            "Auto-Router Gratis": "openrouter/free"
        }
        
        # Valores por defecto iniciales
        self.API_KEY = ""
        self.MODEL = "openai/gpt-oss-120b:free"
        self.SOURCE_LANG = "auto"
        self.TARGET_LANG = "Spanish"
        self.CONTEXT_MODE = False
        self.TRANSLATION_MODE = "AI" # Opciones: "AI", "Fast"
        self.FAST_ENGINE = "google" # Opciones: "google", "bing", "alibaba", etc.
        
        self.load()

    def load(self):
        if os.path.exists(self.CONFIG_FILE):
            try:
                with open(self.CONFIG_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.API_KEY = data.get("api_key", self.API_KEY)
                    self.MODEL = data.get("model", self.MODEL)
                    self.SOURCE_LANG = data.get("source_lang", self.SOURCE_LANG)
                    self.TARGET_LANG = data.get("target_lang", self.TARGET_LANG)
                    self.CONTEXT_MODE = data.get("context_mode", self.CONTEXT_MODE)
                    self.TRANSLATION_MODE = data.get("translation_mode", self.TRANSLATION_MODE)
                    self.FAST_ENGINE = data.get("fast_engine", self.FAST_ENGINE)
                print(f"[Config] Cargada configuración desde {self.CONFIG_FILE}", flush=True)
            except Exception as e:
                print(f"[Config] Error al cargar: {e}", flush=True)

    def save(self, source_lang=None, target_lang=None, model=None, api_key=None, context_mode=None, translation_mode=None, fast_engine=None):
        if source_lang: self.SOURCE_LANG = source_lang
        if target_lang: self.TARGET_LANG = target_lang
        if model: self.MODEL = model
        if api_key is not None: self.API_KEY = api_key
        if context_mode is not None: self.CONTEXT_MODE = context_mode
        if translation_mode: self.TRANSLATION_MODE = translation_mode
        if fast_engine: self.FAST_ENGINE = fast_engine
        
        data = {
            "api_key": self.API_KEY,
            "model": self.MODEL,
            "source_lang": self.SOURCE_LANG,
            "target_lang": self.TARGET_LANG,
            "context_mode": self.CONTEXT_MODE,
            "translation_mode": self.TRANSLATION_MODE,
            "fast_engine": self.FAST_ENGINE
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
