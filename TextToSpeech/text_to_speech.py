import concurrent.futures
import pyttsx3
import time
import sys


def textToSpeech(text, rate=150):
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    engine.setProperty('rate', rate)
    engine.say(text)
    engine.runAndWait()
    del engine


def parallel(text):
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        executor.submit(textToSpeech, text)


parallel("The speed limit is 35 MPH")
time.sleep(4)
textToSpeech("Stop sign")
# time.sleep(5)
textToSpeech("Yield")
