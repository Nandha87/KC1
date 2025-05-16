from luma.core.interface.serial import spi
from luma.oled.device import ssd1309
from luma.core.render import canvas
from PIL import ImageFont
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import tempfile
import os
import time

# --- OLED setup ---
serial = spi(device=0, port=0, gpio_DC=25, gpio_RST=27)
device = ssd1309(serial, width=128, height=64)

# --- Load font ---
try:
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 14)
except:
    font = ImageFont.load_default()

line_height = font.getsize("A")[1] + 2
translator = Translator()
recognizer = sr.Recognizer()

# --- Speak German Translation ---
def speak_translation(text):
    try:
        tts = gTTS(text=text, lang='de')
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp:
            tts.save(tmp.name)
            os.system(f"mpg123 {tmp.name}")
            os.remove(tmp.name)
    except Exception as e:
        print(f"Error speaking translation: {e}")

# --- Recognize English Speech ---
def recognize_speech():
    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("🎙️ Speak in English...")
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=6)
            return recognizer.recognize_google(audio)
        except:
            return None

# --- Translate to German ---
def translate_to_german(text):
    try:
        return translator.translate(text, src='en', dest='de').text
    except Exception as e:
        return f"Translation failed: {e}"

# --- Display Text on OLED ---
def display_text(text):
    lines = text.split('\n')
    wrapped = []
    for line in lines:
        words = line.split(' ')
        current = ''
        for word in words:
            test_line = current + word + ' '
            if font.getsize(test_line)[0] > device.width:
                wrapped.append(current)
                current = word + ' '
            else:
                current = test_line
        wrapped.append(current)

    with canvas(device) as draw:
        y = 0
        for line in wrapped:
            if y + line_height > device.height:
                break
            draw.text((0, y), line.strip(), fill="white", font=font)
            y += line_height

# --- Main loop ---
def run_translator_gui():
    while True:
        spoken = recognize_speech()
        if spoken:
            if "stop translation" in spoken.lower():
                print("Translation stopped.")
                break
            translated = translate_to_german(spoken)
            display_text(translated)
            speak_translation(translated)
        time.sleep(0.5)

# --- Entry point ---
if __name__ == "__main__":
    run_translator_gui()
