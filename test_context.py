import time
import sys
import os
import ctranslate2
import transformers

model_dir = os.path.join(os.path.dirname(__file__), "models", "gemma-2b-ct2")

print("Cargando tokenizer de Gemma 3...")
tokenizer = transformers.AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
print("Cargando modelo en CPU (esto toma unos segundos)...")
model = ctranslate2.Generator(model_dir, device="cpu", compute_type="int8")

story_chunks = [
    "The old detective walked into the dark alley, holding nothing but a flickering flashlight.",
    "He had been warned about the phantom that stalked these streets, but he dismissed it as a fairy tale.",
    "Suddenly, a cold breeze sent a shiver down his spine. The streetlights flickered and died.",
    "Out of the shadows emerged a figure wearing a trench coat. It didn't walk; it seemed to glide.",
    "The detective pulled his gun, but his hands were shaking so much he could barely aim. 'Who are you?' he stammered."
]

# El system prompt siempre queda fijo al principio
history = [
    {"role": "system", "content": "You are a professional translator. Translate the user's text from English to Spanish. Maintain the tone and context of a novel. Reply ONLY with the exact translation. No notes or explanations."}
]

print("\n" + "="*50)
print("INICIANDO PRUEBA DE CONTEXTO ACUMULATIVO (HISTORIAL)")
print("="*50)

for i, chunk in enumerate(story_chunks):
    print(f"\n[Turno {i+1} - Mensajes en memoria: {len(history)}]")
    print(f"Original: {chunk}")
    
    current_prompt = f"Translate to Spanish: {chunk}"
    history.append({"role": "user", "content": current_prompt})
    
    token_ids = tokenizer.apply_chat_template(history, tokenize=True, add_generation_prompt=True, return_dict=False)
    if isinstance(token_ids, dict) and "input_ids" in token_ids:
        token_ids = token_ids["input_ids"]
        
    source = tokenizer.convert_ids_to_tokens(token_ids)
    
    start = time.time()
    results = model.generate_batch(
        [source], 
        max_length=512,
        sampling_temperature=0.0,
        repetition_penalty=1.2,
        include_prompt_in_result=False
    )
    end = time.time()
    
    target = results[0].sequences[0]
    translation = tokenizer.decode(tokenizer.convert_tokens_to_ids(target)).strip()
    
    print(f"Traducción: {translation}")
    print(f"Demora: {end - start:.2f} segundos")
    
    # Guardamos la respuesta en el historial para que Gemma la "recuerde" en el próximo turno
    history.append({"role": "assistant", "content": translation})
