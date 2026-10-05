import json, queue, time, os, subprocess, webbrowser
import sounddevice as sd
from vosk import Model, KaldiRecognizer
import pyautogui
import pygetwindow as gw

MODEL_PATH = "vosk-model-small-hi-0.22"
SAMPLE_RATE = 16000
HOTWORD = "orvex"

# Custom app paths (add yours)
APPS = {
    "chrome": "chrome.exe",
    "vs code": "code",
    "notepad": "notepad.exe",
    "calculator": "calc.exe",
    "explorer": "explorer.exe"
}

# Custom folders
FOLDERS = {
    "downloads": r"C:\Users\%USERNAME%\Downloads",
    "projects": r"D:\Projects",
}

def open_app(app_key):
    if app_key in APPS:
        subprocess.Popen(APPS[app_key])

def close_app(app_key):
    # Try taskkill by common process names
    if app_key == "chrome":
        os.system("taskkill /f /im chrome.exe")
    elif app_key == "vs code":
        os.system("taskkill /f /im Code.exe")
    elif app_key == "notepad":
        os.system("taskkill /f /im notepad.exe")

def open_folder(folder_key):
    if folder_key in FOLDERS:
        subprocess.Popen(rf'explorer {FOLDERS[folder_key]}')

def handle_command(text):
    t = text.lower().strip()
    print("Command:", t)

    # ---- SYSTEM ----
    if "shutdown" in t or "shutdown karo" in t:
        os.system("shutdown /s /t 5")
    elif "restart" in t or "restart karo" in t:
        os.system("shutdown /r /t 5")
    elif "lock" in t or "lock karo" in t:
        os.system("rundll32.exe user32.dll,LockWorkStation")
    elif "sleep" in t:
        os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")

    # ---- VOLUME ----
    elif "volume up" in t or "awaz badhao" in t:
        pyautogui.press("volumeup")
    elif "volume down" in t or "awaz kam" in t:
        pyautogui.press("volumedown")
    elif "mute" in t or "awaz band" in t:
        pyautogui.press("volumemute")

    # ---- WINDOW CONTROL ----
    elif "close window" in t or "window band" in t:
        pyautogui.hotkey("alt", "f4")
    elif "switch window" in t or "window badlo" in t:
        pyautogui.hotkey("alt", "tab")
    elif "minimize" in t:
        pyautogui.hotkey("win", "down")
    elif "maximize" in t:
        pyautogui.hotkey("win", "up")
    elif "show desktop" in t:
        pyautogui.hotkey("win", "d")

    # ---- TYPING ----
    elif t.startswith("type "):
        msg = t.replace("type ", "", 1)
        pyautogui.write(msg)

    # ---- APPS ----
    elif "open chrome" in t or "chrome kholo" in t:
        open_app("chrome")
    elif "close chrome" in t:
        close_app("chrome")

    elif "open vs code" in t or "vscode kholo" in t:
        open_app("vs code")
    elif "close vs code" in t:
        close_app("vs code")

    elif "open notepad" in t or "notepad kholo" in t:
        open_app("notepad")
    elif "open calculator" in t or "calculator kholo" in t:
        open_app("calculator")

    # ---- BROWSER ----
    elif "open youtube" in t or "youtube kholo" in t:
        webbrowser.open("https://www.youtube.com")
    elif "open gmail" in t or "gmail kholo" in t:
        webbrowser.open("https://mail.google.com")
    elif t.startswith("search "):
        query = t.replace("search ", "", 1)
        webbrowser.open(f"https://www.google.com/search?q={query}")
    elif "search" in t:
        # example: "search karo cricket"
        query = t.split("search", 1)[1].strip()
        if query:
            webbrowser.open(f"https://www.google.com/search?q={query}")

    # ---- FILES/FOLDERS ----
    elif "open downloads" in t or "downloads kholo" in t:
        open_folder("downloads")
    elif "open projects" in t or "projects kholo" in t:
        open_folder("projects")

    # ---- MEDIA KEYS ----
    elif "play" in t or "pause" in t:
        pyautogui.press("playpause")
    elif "next" in t:
        pyautogui.press("nexttrack")
    elif "previous" in t:
        pyautogui.press("prevtrack")

    # ---- SCREENSHOT ----
    elif "screenshot" in t:
        pyautogui.screenshot(f"screenshot_{int(time.time())}.png")

    # ---- EXIT ----
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
                    command_timeout = time.time() + 6
                    print("✅ Hotword detected! बोलो command...")
                elif listening_for_command and time.time() <= command_timeout:
                    handle_command(text)
                    listening_for_command = False

if __name__ == "__main__":
    main()