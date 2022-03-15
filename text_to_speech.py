import pyttsx3
import threading


text_to_speech_threads = []
text_to_speech_running = False


def text_to_speech(text, rate=150):
    global text_to_speech_running
    if not text_to_speech_running:
        text_to_speech_running = True
        engine = pyttsx3.init()
        engine.setProperty('volume', 1)
        engine.setProperty('rate', rate)
        engine.say(text)
        engine.runAndWait()
        del engine
        text_to_speech_running = False


def parallel(text):
    thread = threading.Thread(target=text_to_speech, args=(text,), daemon=False)
    thread.start()
    text_to_speech_threads.append(thread)
