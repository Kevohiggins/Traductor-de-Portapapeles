import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from src.translator import translator
import time

print("Esperando a que el traductor cargue...")
while not translator.is_loaded:
    time.sleep(0.5)

prompt = "<start_of_turn>user\nTranslate the following text from English to Spanish. Reply ONLY with the exact translation. Do not add any notes, quotes, or explanations.\n\nText: Hello, world!<end_of_turn>\n<start_of_turn>model\n"
tokens = translator.tokenizer.convert_ids_to_tokens(translator.tokenizer.encode(prompt, add_special_tokens=False))
print("NUESTRO ENCODE:")
print(tokens[:10])

messages = [
    {"role": "user", "content": "Translate the following text from English to Spanish. Reply ONLY with the exact translation. Do not add any notes, quotes, or explanations.\n\nText: Hello, world!"}
]
chat_prompt = translator.tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
print("\nCHAT PROMPT DE HUGGINGFACE:\n" + chat_prompt)
chat_tokens = translator.tokenizer.convert_ids_to_tokens(translator.tokenizer.encode(chat_prompt, add_special_tokens=False))
print("\nENCODE DE HUGGINGFACE:")
print(chat_tokens[:10])
