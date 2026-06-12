import httpx
import json
import os
import translators as ts
from .config import config

class Translator:
    def __init__(self):
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.session = httpx.Client(http2=True)
        self.history_file = os.path.join(config.base_dir, "context_history.json")
        self.history = self._load_history()
        self._last_api_key = None
        self._update_headers()
        # Pre-request de calentamiento
        self._warmup_engines()

    def _load_history(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return []

    def _save_history(self):
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False)
        except Exception:
            pass

    def _warmup_engines(self):
        # Inicializa motores e invoca conexión HTTPS en fondo
        import threading
        def _warmup():
            try:
                ts.translate_text("Hi", from_language="en", to_language="es", engine=config.FAST_ENGINE)
            except:
                pass
            if config.API_KEY:
                try:
                    self.session.get("https://openrouter.ai/api/v1/models", timeout=5)
                    print("[Translator] Warm-up de conexión OpenRouter completado.", flush=True)
                except:
                    pass
        threading.Thread(target=_warmup, daemon=True).start()

    def _update_headers(self):
        if config.API_KEY == self._last_api_key:
            return
            
        self.headers = {
            "Authorization": f"Bearer {config.API_KEY}",
            "Content-Type": "application/json",
            "X-OpenRouter-Title": "Traductor del Portapapeles",
        }
        self.session.headers.update(self.headers)
        self._last_api_key = config.API_KEY

    def translate(self, text, source_lang=None, target_lang=None):
        if not text or not text.strip():
            return ""

        # Elegir modo de traducción
        if config.TRANSLATION_MODE == "Fast":
            return self._translate_fast(text, source_lang, target_lang)
        else:
            return self._translate_ai(text, source_lang, target_lang)

    def _translate_fast(self, text, source_lang=None, target_lang=None):
        try:
            sl = source_lang or config.SOURCE_LANG
            tl = target_lang or config.TARGET_LANG
            
            # Mapeo de códigos de idioma para motores tradicionales (ej. 'Spanish' -> 'es')
            lang_map = {"Spanish": "es", "English": "en", "French": "fr", "German": "de", "auto": "auto"}
            from_lang = lang_map.get(sl, "auto")
            to_lang = lang_map.get(tl, "es")

            # Traducción directa usando motores como Google, Bing, etc.
            result = ts.translate_text(
                text, 
                from_language=from_lang, 
                to_language=to_lang, 
                engine=config.FAST_ENGINE
            )
            return result
        except Exception as e:
            print(f"[FastMode] Error: {e}", flush=True)
            # Fallback a modo AI si falla el rápido
            return self._translate_ai(text, source_lang, target_lang)

    def _translate_ai(self, text, source_lang=None, target_lang=None):
        self._update_headers()
        
        if not config.API_KEY:
            return "Error: No API Key"

        sl = source_lang or config.SOURCE_LANG
        tl = target_lang or config.TARGET_LANG
        
        # System prompt ultra-optimizado para traducción pura y dura
        system_content = (
            f"You are a professional literal translator. Your goal is to translate text from {sl} to {tl} "
            "maintaining the exact tone and style. DO NOT add explanations, notes, or quotes. "
            "If the text is already in the target language, return it as is."
        )

        messages = [{"role": "system", "content": system_content}]

        if config.CONTEXT_MODE and self.history:
            messages.extend(self.history)

        messages.append({"role": "user", "content": text})

        payload = {
            "model": config.MODEL,
            "messages": messages,
            "temperature": 0.3,
            "max_tokens": 2000
        }

        try:
            response = self.session.post(self.url, json=payload, timeout=10)
            
            if response.status_code != 200:
                try:
                    error_msg = response.json().get('error', {}).get('message', '')
                except:
                    error_msg = response.text[:100]
                return f"Error API {response.status_code}: {error_msg}"
                
            data = response.json()
            translation = data['choices'][0]['message']['content'].strip()
            
            if config.CONTEXT_MODE:
                self.history.append({"role": "user", "content": text})
                self.history.append({"role": "assistant", "content": translation})
                self._save_history()
                
            return translation
        except json.JSONDecodeError:
            return "Error: Respuesta inválida (posible caída del servidor)"
        except Exception as e:
            return f"Error de conexión: {e}"

    def clear_history(self):
        self.history = []
        self._save_history()
        print("[Translator] Historial vaciado.", flush=True)

translator = Translator()
