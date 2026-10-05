import json, queue, time, os, subprocess, webbrowser
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import pyautogui

MODEL_PATH = "vosk-model-small-hi-0.22"
SAMPLE_RATE = 16000
HOTWORD = "orvex"

# Commands mapping (Hindi + English)
def handle_command(text):
    t = text.lower().strip()
    print("Command:", t)

    # Apps
    if "open chrome" in t or "chrome kholo" in t:
        subprocess.Popen("chrome.exe")
    elif "open vs code" in t or "open vscode" in t or "vs code kholo" in t:
        subprocess.Popen("code")

    # System
    elif "shutdown" in t or "shutdown karo" in t:
        os.system("shutdown /s /t 5")
    elif "restart" in t or "restart karo" in t:
        os.system("shutdown /r /t 5")

    # Volume
    elif "volume up" in t or "awaz badhao" in t:
        pyautogui.press("volumeup")
    elif "volume down" in t or "awaz kam" in t:
        pyautogui.press("volumedown")
    elif "mute" in t or "awaz band" in t:
        pyautogui.press("volumemute")

    # Browser
    elif "open youtube" in t or "youtube kholo" in t:
        webbrowser.open("https://www.youtube.com")
    elif "open gmail" in t or "gmail kholo" in t:
        webbrowser.open("https://mail.google.com")
    elif t.startswith("search "):
        query = t.replace("search ", "", 1)
        webbrowser.open(f"https://www.google.com/search?q={query}")
    elif "search" in t and " " in t:
        # Hindi search: "search करो cricket"
        query = t.split("search",1)[1].strip()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query}")

    # Folders
    elif "open downloads" in t or "downloads kholo" in t:
        subprocess.Popen(r"explorer C:\Users\%USERNAME%\Downloads")
    elif "open projects" in t or "projects kholo" in t:
        subprocess.Popen(r"explorer D:\Projects")

    # Exit
    elif "exit program" in t or "band karo" in t:
        print("Exiting...")
        os._exit(0)

# Audio pipeline
q = queue.Queue()

def callback(indata, frames, time_info, status):
    q.put(bytes(indata))

def main():
    model = Model(MODEL_PATH)
    rec = KaldiRecognizer(model, SAMPLE_RATE)

    with sd.RawInputStream(samplerate=SAMPLE_RATE, blocksize=8000, dtype='int16',
                           channels=1, callback=callback):
        print(f"🎤 Listening... Say '{HOTWORD}' to activate.")
        listening_for_command = False
        command_timeout = 0

        while True:
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if not text:
                    continue

                if HOTWORD in text:
                    listening_for_command = True
                    command_timeout = time.time() + 5
                    print("✅ Hotword detected! बोलो command...")

                elif listening_for_command and time.time() <= command_timeout:
                    handle_command(text)
                    listening_for_command = False

if __name__ == "__main__":
    main()