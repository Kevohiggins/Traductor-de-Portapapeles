from accessible_output2.outputs.auto import Auto

class TTS:
    def __init__(self):
        try:
            self.speaker = Auto()
            print("[TTS] Motor de salida accesible inicializado correctamente.", flush=True)
        except Exception as e:
            print(f"[TTS] Error inicializando accessible_output2: {e}", flush=True)
            self.speaker = None

    def speak(self, text, interrupt=True):
        if not text or not self.speaker:
            return

        try:
            # accessible_output2 maneja internamente NVDA, JAWS, SAPI, etc.
            self.speaker.speak(text, interrupt=interrupt)
        except Exception as e:
            print(f"[TTS] Error al verbalizar: {e}", flush=True)

tts = TTS()
