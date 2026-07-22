import os
import threading
from .config import config
from .languages import NLLB_LANGUAGES, GEMMA_LANGUAGES

class Translator:
    def __init__(self):
        # Local AI variables
        self.model = None
        self.tokenizer = None
        self.is_loaded = False
        self.translation_history = []
        self._init_local_ai()

    def _init_local_ai(self):
        def _load():
            try:
                import ctranslate2
                import transformers
                
                print("[Translator] Cargando tokenizer de Gemma...", flush=True)
                self.tokenizer = transformers.AutoTokenizer.from_pretrained(config.MODEL_DIR, local_files_only=True)
                
                print("[Translator] Cargando modelo Gemma en procesador (CTranslate2)...", flush=True)
                self.model = ctranslate2.Generator(config.MODEL_DIR, device="cpu", compute_type="int8")
                self.is_loaded = True
                print("[Translator] ¡Gemma cargado exitosamente!", flush=True)
                
            except Exception as e:
                import traceback
                error_msg = f"Error grave al cargar modelo: {e}\n{traceback.format_exc()}"
                print(f"[Translator] {error_msg}", flush=True)
                with open("error_log.txt", "w", encoding="utf-8") as f:
                    f.write(error_msg)

        threading.Thread(target=_load, daemon=True).start()

    def translate(self, text, source_lang=None, target_lang=None):
        if not text or not text.strip():
            return ""

        if not self.model or not self.tokenizer:
            return "El modelo de traducción local todavía se está cargando. Esperá unos segundos y volvé a intentarlo."

        sl = source_lang or config.SOURCE_LANG
        tl = target_lang or config.TARGET_LANG
        
        try:
            import re
            
            # Separar SOLO por saltos de línea para mantener el contexto
            chunks = re.split(r'(\n+)', text)
            
            sources = []
            chunk_indices = []
            added_periods = []
            
            for i, chunk in enumerate(chunks):
                if chunk and not chunk.isspace():
                    # Evitar alucinaciones en oraciones sin terminar
                    added_period = False
                    if not chunk.endswith((".", "!", "?", ":", ";", '"', "'")):
                        chunk += "."
                        added_period = True
                        
                    
                    sl_english = GEMMA_LANGUAGES.get(sl, "English")
                    tl_english = GEMMA_LANGUAGES.get(tl, "Spanish")
                    
                    if not config.USE_CONTEXT:
                        self.translation_history.clear()
                        
                    messages = []
                    instruction = f"Translate the following text from {sl_english} to {tl_english}. Pay special attention to idioms, ironies, double meanings, and non-literal phrases; translate their intended meaning naturally into {tl_english} rather than doing a word-for-word literal translation. Reply ONLY with the exact translation. Do not add any notes, quotes, or explanations."
                    
                    messages.append({"role": "system", "content": instruction})
                    
                    if config.USE_CONTEXT:
                        for orig, trans in self.translation_history:
                            messages.append({"role": "user", "content": orig})
                            messages.append({"role": "assistant", "content": trans})
                    
                    messages.append({"role": "user", "content": chunk})
                    
                    token_ids = self.tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_dict=False)
                    if isinstance(token_ids, dict) and "input_ids" in token_ids:
                        token_ids = token_ids["input_ids"]
                    
                    source = self.tokenizer.convert_ids_to_tokens(token_ids)
                    
                    sources.append(source)
                    chunk_indices.append(i)
                    added_periods.append(added_period)
            
            if sources:
                # Usar generate_batch en lugar de translate_batch
                results = self.model.generate_batch(
                    sources, 
                    max_length=1024,
                    sampling_temperature=0.0,  # Greedy decoding para mayor precisión
                    repetition_penalty=1.2,
                    include_prompt_in_result=False
                )
                
                # Volcar traducciones en sus lugares originales
                for idx_in_batch, original_idx in enumerate(chunk_indices):
                    target = results[idx_in_batch].sequences[0]
                    translation = self.tokenizer.decode(self.tokenizer.convert_tokens_to_ids(target)).strip()
                    
                    original_text = chunks[original_idx]
                    
                    if added_periods[idx_in_batch] and translation.endswith("."):
                        translation = translation[:-1]
                        
                    chunks[original_idx] = translation
                    
                    if config.USE_CONTEXT:
                        if added_periods[idx_in_batch] and original_text.endswith("."):
                            original_text = original_text[:-1] # Remove added period for history matching
                        self.translation_history.append((original_text, translation))
                        if len(self.translation_history) > 10:
                            self.translation_history.pop(0)
                            
            return "".join(chunks)
        except Exception as e:
            return f"Error interno del modelo local: {e}"

translator = Translator()
