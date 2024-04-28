import os

import certifi
import pyttsx3
import speech_recognition as sr

os.environ["SSL_CERT_FILE"] = certifi.where()

engine = pyttsx3.init()
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[41].id)
# 0, 7, 10, 11, 28, 32, 33, 37, 40, 41 - english voices (mac)

KEYWORD_LIST = ["rhea", "ria", "riaa", "riya", "riyaa"]


engine.say("Hi! I am Rhea, your virtual assistant!")
engine.runAndWait()


def take_command():
    """ """
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        r.pause_threshold = 1
        audio = r.listen(source)

    try:
        print("Recognizing...")
        # query = r.recognize_sphinx(audio)
        query = r.recognize_whisper(audio, language="english", model="base")
        print(f"User said: {query}\n")
        engine.say(f"You said: {query}")
        engine.runAndWait()

    except Exception as e:
        print(e)
        print("Say that again please...")
        return "None"
    return query


def process_command(cmd: str):
    """

    :param cmd: str:

    """
    engine.say(f"You said {cmd}")


if __name__ == "__main__":
    while True:
        command = take_command().lower()
        if any(word.lower() in command for word in KEYWORD_LIST):
            process_command(command)
