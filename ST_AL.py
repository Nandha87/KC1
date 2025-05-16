import logging
import os
import sys
import speech_recognition as sr
from googletrans import Translator
from gtts import gTTS
import pygame
import time
import subprocess


class SpeechTranslatorActionLibrary:
    def __init__(self, log_file_path=None):
        self.recognizer = sr.Recognizer()
        self.logger = self.setup_logger(log_file_path)
        self.gui_process = None

    def setup_logger(self, log_file_path):
        logger = logging.getLogger("SpeechTranslator")
        logger.setLevel(logging.DEBUG)

        if logger.hasHandlers():
            logger.handlers.clear()

        # Default to home directory logs folder if no path is given
        if not log_file_path:
            home_dir = os.path.expanduser("~")
            log_file_path = os.path.join(home_dir, "logs", "speech_translation.log")

        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)

        with open(log_file_path, "w", encoding="utf-8"):
            pass

        print(f"📂 Logs will be saved to: {log_file_path}")
        file_handler = logging.FileHandler(log_file_path, mode='a', encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        return logger

    def start_gui(self):
        try:
            self.logger.info("Starting GUI application...")
            self.gui_process = subprocess.Popen(["python", "ST_GUI.py"])
        except Exception as e:
            self.logger.error(f"Failed to start GUI: {e}")

    def stop_gui(self):
        if self.gui_process:
            self.gui_process.terminate()
            self.logger.info("Stopped GUI application.")

    def test_microphone(self):
        try:
            with sr.Microphone() as source:
                self.logger.info("Testing microphone...")
                print("Testing microphone... Speak now!")
                self.recognizer.adjust_for_ambient_noise(source, duration=2)
                print("Microphone is working.")
                return True
        except Exception as e:
            self.logger.error(f"Microphone test failed: {e}")
            print(f"Microphone test failed: {e}")
            return False

    def convert_speech_to_text(self):
        self.logger.info("Starting real-time translation...")
        print("App started. Say 'start translation' to begin.")

        started = False
        last_speech_time = time.time()
        max_retries = 3
        retry_count = 0

        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=1)

            while True:
                try:
                    print("Listening...")
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                    text = self.recognizer.recognize_google(audio).lower().strip()
                    print(f"You said: {text}")
                    self.logger.info(f"Recognized: {text}")
                    retry_count = 0  # Reset retry count on successful recognition

                    if not started:
                        if "start translation" in text:
                            print("Start command detected. Waiting for next input...")
                            self.logger.info("Start command received.")
                            started = True
                        continue

                    if "stop translation" in text:
                        print("Detected stop command. Stopping translation...")
                        self.logger.info("Stop command received.")
                        return "STOP"

                    translated_text = self.translate_text(text, from_lang="en", to_lang="hi")
                    if translated_text:
                        print(f"Translated: {translated_text}")
                        self.convert_text_to_speech(translated_text, lang="hi")

                    last_speech_time = time.time()

                except sr.UnknownValueError:
                    print("Could not understand audio. Speak clearly...")
                except sr.RequestError as e:
                    self.logger.error(f"Google Speech Recognition error: {e}")
                    retry_count += 1
                    if retry_count >= max_retries:
                        print("Too many failed attempts. Stopping translation.")
                        break
                    print(f"Retrying... (Attempt {retry_count}/{max_retries})")
                    time.sleep(1)  # Wait a bit before retrying
                except Exception as e:
                    self.logger.error(f"Error: {e}")
                    print("Error:", e)
                    break

                if time.time() - last_speech_time > 10:
                    print("No speech detected for 10 seconds. Stopping translation.")
                    break

    def translate_text(self, text, from_lang="en", to_lang="hi"):
        self.logger.info(f"Translating text: {text} from {from_lang} to {to_lang}")
        try:
            translator = Translator()
            return translator.translate(text, src=from_lang, dest=to_lang).text
        except Exception as e:
            self.logger.error(f"Error during translation: {e}")
            print(f"Translation error: {e}")
            return None

    def suppress_pygame_messages(self):
        null_file = open(os.devnull, "w")
        old_stdout = sys.stdout
        sys.stdout = null_file
        pygame.mixer.init()
        sys.stdout = old_stdout

    def convert_text_to_speech(self, text, lang="hi"):
        self.logger.info(f"Converting text to speech: {text}")
        temp_file = "temp_speech.mp3"
        try:
            self.suppress_pygame_messages()
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(temp_file)
            pygame.mixer.music.load(temp_file)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            pygame.mixer.music.unload()
        except Exception as e:
            self.logger.error(f"Error during text-to-speech: {e}")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def execute_translation_workflow(self):
        self.logger.info("Executing real-time translation workflow...")
        self.start_gui()
        # Add a delay to ensure GUI has time to initialize
        time.sleep(2)
        
        if not self.test_microphone():
            print("Microphone issue. Check settings.")
            self.stop_gui()
            return
            
        try:
            self.convert_speech_to_text()
        except KeyboardInterrupt:
            print("\nTranslation stopped by user.")
        finally:
            self.stop_gui()
            print("Real-time translation stopped.")


if __name__ == "__main__":
    # Automatically use the user's home directory for log storage
    home_dir = os.path.expanduser("~")
    log_dir = os.path.join(home_dir, "logs")
    custom_log_path = os.path.join(log_dir, "speech_translation.log")

    translator = SpeechTranslatorActionLibrary(log_file_path=custom_log_path)
    translator.execute_translation_workflow()