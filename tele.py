# tele.py
import time
import os
import textwrap
import requests
import multiprocessing
from dotenv import load_dotenv
import speech_recognition as sr

from tele_GUI import start_teleprompter  # Import the OLED teleprompter

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# === Module 1: Text Generation (Gemini API Integration) ===
def generate_script(prompt, retries=5, delay=5):
    refined_prompt = f"Write a long, detailed teleprompter script in smooth paragraph style (no bullet points) about this topic: {prompt}. The script should be at least 500 words and sound natural when read aloud."
    
    api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {
        "Content-Type": "application/json"
    }
    payload = {
        "contents": [
            {
                "parts": [
                    {"text": refined_prompt}
                ]
            }
        ]
    }

    for attempt in range(retries):
        try:
            response = requests.post(api_url, headers=headers, json=payload)
            if response.status_code == 429:
                print("⚠ Rate limited. Retrying after delay...")
                time.sleep(delay)
                delay *= 2
                continue
            response.raise_for_status()
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except requests.RequestException as e:
            print(f"Error on attempt {attempt + 1}: {e}")
            time.sleep(delay)
            delay *= 2

    return "[Error] Failed to generate script."

# === Module 2: Save Generated Text as .txt File ===
def save_script_to_file(title, content):
    os.makedirs("scripts", exist_ok=True)
    filename = f"scripts/{title}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f" Script saved as '{filename}'.")
    return filename

def load_script_from_file(title):
    filename = f"scripts/{title}.txt"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    else:
        print("⚠ Script file not found.")
        return None

# === Module 3: Teleprompter Viewer in Terminal (optional) ===
def run_teleprompter(script_text, speed=0.5, width=70):
    wrapped_text = textwrap.wrap(script_text, width)
    print("\n--- Teleprompter Started ---\n")
    for line in wrapped_text:
        print(line)
        time.sleep(speed)
    print("\n--- End of Script ---\n")

# === Module 4: Voice Input Setup ===
def listen_for_prompt():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print("Listening... Please speak your prompt:")
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source)
        
        try:
            prompt = r.recognize_google(audio)
            print(f"You said: {prompt}")
            return prompt
        except sr.UnknownValueError:
            print(" Could not understand your voice. Please try again.")
            return None
        except sr.RequestError:
            print(" Speech recognition service unavailable.")
            return None

# === Main Execution Flow ===
def main():
    print("Welcome to Voice-based Teleprompter 🎬")
    
    prompt = listen_for_prompt()
    
    if prompt is None:
        return
    
    # Generate Script
    generated = generate_script(prompt)

    if "[Error]" in generated:
        print(" Script generation failed. Please try again later.")
        return

    # Save Script to File
    title = f"script_{int(time.time())}"
    filepath = save_script_to_file(title, generated)

    print("\nLoading the latest script for teleprompter...")

    script = load_script_from_file(title)
    if script:
        # (Optional) Run in terminal
        run_teleprompter(script)
        
        print(" Starting OLED teleprompter GUI...")
        p = multiprocessing.Process(target=start_teleprompter, args=(filepath,))
        p.start()

        # Keep main program alive until OLED finishes (optional)
        p.join()
    else:
        print(" Could not load the script.")

if __name__ == "__main__":
    main()
