import os
import sys

try:
    import ctranslate2
except ImportError:
    print("Error: Necesitas instalar ctranslate2 y torch para convertir el modelo.")
    print("Ejecuta: pip install ctranslate2 torch transformers")
    sys.exit(1)

def download_and_convert():
    model_id = "facebook/nllb-200-distilled-600M"
    local_dir = os.path.join(os.path.dirname(__file__), "models", "nllb-ct2")

    print(f"Descargando {model_id} oficial y convirtiéndolo a CTranslate2 INT8...")
    print("Esto puede tomar varios minutos y consumir bastante RAM. ¡Paciencia!")
    
    try:
        # El TransformersConverter descarga automáticamente el modelo desde HuggingFace y lo convierte
        converter = ctranslate2.converters.TransformersConverter(
            model_name_or_path=model_id,
            copy_files=["tokenizer.json", "tokenizer_config.json", "special_tokens_map.json"]
        )
        converter.convert(output_dir=local_dir, quantization="int8", force=True)
        print(f"\n[OK] ¡Modelo convertido exitosamente en {local_dir}!")
    except Exception as e:
        print(f"\n[ERROR] Falló la conversión: {e}")

if __name__ == "__main__":
    download_and_convert()
