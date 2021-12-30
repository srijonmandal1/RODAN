import pyttsx3
import threading

def change_voice(engine, language="english"):
    for voice in engine.getProperty('voices'):
        if language == voice.id:
            engine.setProperty('voice', voice.id)
            return True

    raise RuntimeError(f"Language '{language}' not found")


def textToSpeech(text, rate=150):
    engine = pyttsx3.init()
    engine.setProperty('volume', 1)
    change_voice(engine)
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()
    del engine


def parallel(text):
    print(32)
    threading.Thread(target=textToSpeech, args=(text,)).start()
    textToSpeech(text)
