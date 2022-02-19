import pyttsx3
import threading


text_to_speech_threads = []
text_to_speech_running = False


def change_voice(engine, voice_name="english_wmids"):
    for voice in engine.getProperty('voices'):
        if voice.name == voice_name:
            engine.setProperty('voice', voice.id)
            return True

    raise RuntimeError(f"Voice name '{voice_name}' not found")


def textToSpeech(text, rate=150):
    global text_to_speech_running
    if not text_to_speech_running:
        text_to_speech_running = True
        engine = pyttsx3.init()
        engine.setProperty('volume', 1)
        # change_voice(engine)
        engine.setProperty('rate', rate)
        engine.say(text)
        engine.runAndWait()
        del engine
        text_to_speech_running = False


def parallel(text):
    thread = threading.Thread(target=textToSpeech, args=(text,), daemon=False)
    thread.start()
    text_to_speech_threads.append(thread)
