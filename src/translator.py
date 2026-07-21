import os
import threading
from .config import config
from .languages import NLLB_LANGUAGES

class Translator:
    def __init__(self):
        # Local AI variables
        self.model = None
        self.tokenizer = None
        self._init_local_ai()

    def _init_local_ai(self):
        def _load():
            try:
                import ctranslate2
                import transformers
                
                print("[Translator] Cargando tokenizer de Meta NLLB...", flush=True)
                self.tokenizer = transformers.AutoTokenizer.from_pretrained(config.MODEL_DIR, local_files_only=True)
                
                print("[Translator] Cargando modelo NLLB en procesador (CTranslate2)...", flush=True)
                self.model = ctranslate2.Translator(config.MODEL_DIR, device="cpu", compute_type="int8")
                self.is_loaded = True
                print("[Translator] ¡Modelo NLLB cargado exitosamente!", flush=True)
                
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
        
        # Obtener los códigos _Latn/_Cyrl reales desde el diccionario
        src_code = NLLB_LANGUAGES.get(sl, "eng_Latn")
        tgt_code = NLLB_LANGUAGES.get(tl, "spa_Latn")
        
        try:
            import re
            
            if config.SPLIT_SENTENCES:
                # Divide por oraciones o saltos de línea manteniendo los separadores
                chunks = re.split(r'([.!?]+\s+|\n+)', text)
            else:
                # Separar SOLO por saltos de línea para mantener el contexto
                chunks = re.split(r'(\n+)', text)
            
            sources = []
            chunk_indices = []
            added_periods = []
            
            self.tokenizer.src_lang = src_code
            
            # Preparar el batch de párrafos
            for i, chunk in enumerate(chunks):
                if chunk and not chunk.isspace():
                    # Evitar alucinaciones en oraciones sin terminar
                    added_period = False
                    if not chunk.endswith((".", "!", "?", ":", ";", '"', "'")):
                        chunk += "."
                        added_period = True
                        
                    source = self.tokenizer.convert_ids_to_tokens(self.tokenizer.encode(chunk))
                    sources.append(source)
                    chunk_indices.append(i)
                    added_periods.append(added_period)
            
            if sources:
                target_prefixes = [[tgt_code]] * len(sources)
                # Aplicamos los parámetros maestros para evitar que NLLB omita texto:
                # - coverage_penalty: Castiga matemáticamente al modelo si ignora palabras del origen.
                # - max_decoding_length: Aumenta el límite de tokens para que no se corte por límite de memoria.
                results = self.model.translate_batch(
                    sources, 
                    target_prefix=target_prefixes, 
                    beam_size=config.BEAM_SIZE,
                    coverage_penalty=2.0,
                    length_penalty=1.5,
                    repetition_penalty=1.2,
                    max_decoding_length=1024
                )
                
                # Volcar traducciones en sus lugares originales
                for idx_in_batch, original_idx in enumerate(chunk_indices):
                    target = results[idx_in_batch].hypotheses[0][1:]
                    translation = self.tokenizer.decode(self.tokenizer.convert_tokens_to_ids(target))
                    
                    if added_periods[idx_in_batch] and translation.endswith("."):
                        translation = translation[:-1]
                        
                    chunks[original_idx] = translation
                    
            return "".join(chunks)
        except Exception as e:
            return f"Error interno del modelo local: {e}"

translator = Translator()
