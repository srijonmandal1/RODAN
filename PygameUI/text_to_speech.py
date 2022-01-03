import pyttsx3
import threading

def change_voice(engine, language="english"):
    for voice in engine.getProperty('voices'):
        # if language == voice.id:
        if voice.name == "english_wmids":
            engine.setProperty('voice', voice.id)
            return True

    raise RuntimeError(f"Language '{language}' not found")


def textToSpeech(text, rate=150):
    engine = pyttsx3.init()
    for voice in engine.getProperty("voices"):
        print(f"Lang: {voice.languages}")
        print(f"Gender: {voice.gender}")
        print(f"Name: {voice.name}")
    engine.setProperty('volume', 1)
    change_voice(engine)
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()
    del engine


def parallel(text):
    threading.Thread(target=textToSpeech, args=(text,)).start()
