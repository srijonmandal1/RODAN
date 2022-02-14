import pyttsx3
import multiprocessing


text_to_speech_processes = []


def change_voice(engine, voice_name="english_wmids"):
    for voice in engine.getProperty('voices'):
        if voice.name == voice_name:
            engine.setProperty('voice', voice.id)
            return True

    raise RuntimeError(f"Voice name '{voice_name}' not found")


def textToSpeech(text, rate=150):
    engine = pyttsx3.init()
    engine.setProperty('volume', 1)
    change_voice(engine)
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()
    del engine


def parallel(text):
    proc = multiprocessing.Process(target=textToSpeech, args=(text,))
    proc.start()
    text_to_speech_processes.append(proc)
