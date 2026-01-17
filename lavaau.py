import pyttsx3
import speech_recognition as sr
import datetime
import webbrowser
import os
import sys
import pyaudio
import urllib3
import smtplib
import ssl
import random
import json
import pyjokes
import vlc
import re
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import pvporcupine
from pvrecorder import PvRecorder
import time

load_dotenv("LAVAAPI.env")
GMAIL_EMAIL = os.getenv("GMAIL_EMAIL")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
ACCESS_KEY = os.getenv("PICOVOICE_ACCESS_KEY")
MUSIC_DIR = "C:\\Users\\durga\\OneDrive\\Music\\Playlists" 

wake_word_attempts = 0
wake_word_detected = 0
total_voice_commands = 0
recognized_voice_commands = 0
total_intents = 0
correct_intents = 0
total_latency = 0.0

engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)
engine.setProperty('rate', 180)


KEYWORD_PATH = r"C:\Users\durga\OneDrive\lava\Hey-Lava_en_windows_v4_0_0.ppn"

print("Keyword exists:", os.path.exists(
    r"C:\Users\durga\OneDrive\lava\Hey-Lava_en_windows_v4_0_0.ppn"
))
if not os.path.exists(KEYWORD_PATH):
    print("Keyword file missing")
    sys.exit(1)


porcupine = pvporcupine.create(
    access_key="cIwxLRZf45CMQrEzWDkif3kPtbJGG2swn2oyyUGHKFu2GqS+PIyyQQ==",
    keyword_paths=[KEYWORD_PATH]
)

recorder = PvRecorder(device_index=0, frame_length=porcupine.frame_length)
print(PvRecorder.get_available_devices())

def speak(text, emotion="neutral"):
    emotions = {
        "happy": ["Absolutely fantastic!"],
        "sarcastic": ["Oh wow, another brilliant command!", "Of course, because I have nothing else to do..."],
        "angry": ["I’m not in the mood for this!", "Do you really think I enjoy this job?"],
        "neutral": ["Understood.", "Processing your request."]
    }
    if emotion in emotions:
        text = random.choice(emotions[emotion]) + " " + text
    print(f"LAVA ({emotion.upper()}): {text}")
    engine.say(text)
    engine.runAndWait()

def take_command():
    global total_voice_commands, recognized_voice_commands

    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening...")
        audio = recognizer.listen(source)

    total_voice_commands += 1

    try:
        query = recognizer.recognize_google(audio, language="en-in")
        recognized_voice_commands += 1
        print(f"You said: {query}")
        return query.lower()
    except:
        return "none"


def open_application(query):
    apps = {
        "notepad": "notepad.exe",
        "calculator": "calc.exe",
        "chrome": "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
    }
    for app in apps:
        if app in query:
            os.startfile(apps[app])
            speak(f"Opening {app}", "happy")
            return
    speak("I couldn't find that application.", "angry")
    
def send_email():
    speak("Who should I send the email to? Please say the email address.", "neutral")

    while True:
        recipient_email = take_command().replace(" ", "").lower()

        # Validate email format
        if "@" not in recipient_email or "." not in recipient_email:
            speak("That doesn't seem like a valid email. Please try again.", "angry")
            continue  # Ask for email again
        
        # Confirm email address
        speak(f"Did you say {recipient_email}? Please say yes or no.", "neutral")
        confirmation = take_command().lower()

        if confirmation in ["yes", "yeah", "confirm", "okay", "correct"]:
            break  # Exit loop and proceed
        else:
            speak("Okay, let's try again.", "neutral")

    # Proceed with asking for email content
    speak("Great! What should I say in the email?", "neutral")
    email_content = take_command()

    if not email_content or email_content.lower() == "none":
        speak("I didn't catch that. Please try again.", "angry")
        return

    # Confirm before sending
    speak(f"Just to confirm, you want to send an email to {recipient_email} saying: {email_content}. Should I send it? Say yes or no.", "neutral")
    final_confirmation = take_command().lower()

    if final_confirmation in ["yes", "yeah", "send", "confirm", "okay"]:
        subject = "Email from LAVA"
        message = f"Subject: {subject}\n\n{email_content}"

        try:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
                server.login(GMAIL_EMAIL, GMAIL_APP_PASSWORD)
                server.sendmail(GMAIL_EMAIL, recipient_email, message)
                speak(f"Email sent to {recipient_email}!", "happy")
        except Exception as e:
            speak(f"I was unable to send the email. Error: {e}", "angry")
    else:
        speak("Okay, email sending cancelled.", "neutral")
        
def play_music_on_youtube():
    speak("Which song would you like to play?", "happy")
    song_name = take_command()

    if not song_name:
        speak("I didn't catch that. Please say the song name again.", "angry")
        return

    search_query = song_name.replace(" ", "+")
    search_url = f"https://www.youtube.com/results?search_query={search_query}"

    try:

        response = requests.get(search_url)
        soup = BeautifulSoup(response.text, "html.parser")
        video_links = re.findall(r"\/watch\?v=[a-zA-Z0-9_-]+", str(soup))
        if video_links:
            video_url = f"https://www.youtube.com{video_links[0]}"  # Get the first result
            speak(f"Playing {song_name} on YouTube!", "happy")
            webbrowser.open(video_url)
        else:
            speak("Sorry, I couldn't find that song on YouTube.", "angry")

    except Exception as e:
        speak("There was an error while searching on YouTube.", "angry")
        print("Error:", e)
        
def search_google(query):
    search_term = query.replace("search", "").strip()
    if search_term:
        speak(f"Searching Google for {search_term}", "neutral")
        webbrowser.open(f"https://www.google.com/search?q={search_term}")
    else:
        speak("I didn't catch that. Please try again.", "angry")


def open_website(query):

    websites = {
        "youtube": "https://www.youtube.com",
        "chrome": "https://www.google.com",
        "wikipedia": "https://www.wikipedia.org",
        "stackoverflow": "https://stackoverflow.com"
    }
    for site in websites:
        if site in query:
            webbrowser.open(websites[site])
            speak(f"Opening {site}", "happy")
            return
    speak("I couldn't find that website.", "angry")
    

MUSIC_DIR = r"C:\Users\durga\OneDrive\Music\Playlists"  
def play_music():
    if not os.path.exists(MUSIC_DIR):
        speak("Music directory not found.", "angry")
        return

    songs = [f for f in os.listdir(MUSIC_DIR) if f.endswith(('.mp3', '.wav'))]

    if not songs:
        speak("No music files found.", "angry")
        return

    song = random.choice(songs)
    song_path = os.path.join(MUSIC_DIR, song)
    speak(f"Playing {song}", "happy")

    instance = vlc.Instance()
    player = instance.media_player_new()
    media = instance.media_new(song_path)
    player.set_media(media)
    player.play()

    time.sleep(1)

    while player.get_state() != vlc.State.Ended:
        time.sleep(1)

def listen_for_wake_word():
    global wake_word_attempts, wake_word_detected

    print("Listening for wake word...")
    wake_word_attempts += 1
    recorder.start()

    try:
        while True:
            pcm = recorder.read()
            if porcupine.process(pcm) >= 0:
                recorder.stop()
                wake_word_detected += 1
                print("Wake word detected!")
                return True
    except KeyboardInterrupt:
        recorder.stop()
        return False
    
def handle_intent(query):
    global correct_intents

    if "open" in query:
        correct_intents += 1
        speak("Opening application")
    elif "play" in query:
        correct_intents += 1
        speak("Playing media")
    elif "search" in query:
        correct_intents += 1
        speak("Searching the web")
    elif "time" in query:
        correct_intents += 1
        speak(time.ctime())
    elif "exit" in query or "stop" in query:
        correct_intents += 1
        return "exit"
    else:
        speak("Command not recognized")

    return "continue"

def main():
    global total_intents, total_latency

    speak("LAVA assistant started")

    while True:
        if listen_for_wake_word():
            speak("Yes, how can I help you?")

            start_time = time.time()
            query = take_command()
            total_intents += 1

            if query == "none":
                continue

            result = handle_intent(query)

            end_time = time.time()
            total_latency += (end_time - start_time)

            if result == "exit":
                break
    wake_accuracy = (wake_word_detected / wake_word_attempts) * 100 if wake_word_attempts else 0
    voice_accuracy = (recognized_voice_commands / total_voice_commands) * 100 if total_voice_commands else 0
    intent_accuracy = (correct_intents / total_intents) * 100 if total_intents else 0
    avg_latency = (total_latency / total_intents) if total_intents else 0
           
    print(f"Wake Word Accuracy        : {(wake_word_detected / wake_word_attempts) * 100:.2f}%")
    print(f"Voice Recognition Accuracy: {(recognized_voice_commands / total_voice_commands) * 100:.2f}%")
    print(f"NLP Intent Accuracy       : {(correct_intents / total_intents) * 100:.2f}%")
    print(f"Average Response Latency  : {(total_latency / total_intents):.2f} seconds")

if __name__ == "__main__":
    main()
