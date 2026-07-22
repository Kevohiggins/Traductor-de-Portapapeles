import time
import sys

# Agregar src al path
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.translator import translator

def test_translation(text, sl, tl):
    print("-" * 50)
    print(f"[Test] Longitud: {len(text)} caracteres")
    print(f"Original: {text}")
    start = time.time()
    result = translator.translate(text, source_lang=sl, target_lang=tl)
    end = time.time()
    print(f"Traducción: {result}")
    print(f"Demora: {end - start:.2f} segundos")

print("Cargando modelo en memoria... (Esto puede tomar unos segundos la primera vez)")
while not translator.is_loaded:
    time.sleep(0.5)
print("¡Modelo cargado! Iniciando pruebas...\n")

# Prueba 1: Súper corta (ideal para medir latencia base)
test_translation("Hello, world!", "English", "Spanish")

# Prueba 2: Frase media con contexto
test_translation("Gemma 3 is a highly advanced text generation model developed by Google.", "English", "Spanish")

# Prueba 3: Frase larga y compleja (idioms y sarcasmo)
test_translation("It's raining cats and dogs outside! I can't believe we have to go out in this weather. It's an absolute nightmare.", "English", "Spanish")

# Prueba 4: Frase muy larga (bestial, ~50 palabras)
test_translation("I honestly can't figure out why anyone would want to wake up at five in the morning on a Sunday just to go running in the freezing cold, especially when they could be sleeping peacefully in their warm bed, but I guess some people are just built differently and thrive on that kind of early morning torture.", "English", "Spanish")
