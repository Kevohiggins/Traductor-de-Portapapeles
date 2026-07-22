import time
import sys
import os

sys.path.append(os.path.dirname(__file__))

from src.translator import translator
from src.config import config

# Habilitar el contexto
config.USE_CONTEXT = True

print("Cargando modelo en memoria... (Esto puede tomar unos segundos la primera vez)")
while not getattr(translator, 'is_loaded', False):
    time.sleep(0.5)
print("¡Modelo cargado! Iniciando pruebas...\n")

textos_prueba = [
    "I saw a huge monster in the forest.",
    "It had giant red eyes and sharp teeth.",
    "I tried to run, but it was too fast.",
]

for idx, texto in enumerate(textos_prueba):
    print(f"\n[Texto {idx+1}]")
    print(f"Original: {texto}")
    
    start_time = time.time()
    traduccion = translator.translate(texto, source_lang="Inglés", target_lang="Español")
    end_time = time.time()
    
    print(f"Traducción: {traduccion}")
    print(f"Demora: {end_time - start_time:.2f} segundos")
    print(f"Historial actual: {len(translator.translation_history)} mensajes.")

print("\nDesactivando contexto...")
config.USE_CONTEXT = False
traduccion = translator.translate("This is a new isolated sentence.", source_lang="Inglés", target_lang="Español")
print(f"Traducción sin contexto: {traduccion}")
print(f"Historial actual (debe ser 0): {len(translator.translation_history)}")

print("\n--- PRUEBA FINALIZADA ---")
