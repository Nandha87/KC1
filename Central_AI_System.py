import speech_recognition as sr
from ST_AL import SpeechTranslatorActionLibrary
import languagemodels as lm

import numpy as np
import time
import tele
import threading
from app import main as flet_main
import flet as ft
from Synta import Synta



class CentralAISystem:
    def __init__(self):
        self.recognizer = sr.Recognizer()
        self.stt = SpeechTranslatorActionLibrary()
        self.is_translating = False
        self.llm_enabled = False
        self.synta = Synta()


    def process_command(self, command):
        command = command.lower()
        print(f"Processing command: {command}")

        if "help" in command:
            self._speak("Here's what I can do. Start translation, stop translation, enable A I, stop A I, or ask me anything in A I mode.")
            return

        if "start translation" in command:
            self.is_translating = True
            self.start_translation()
        elif "stop translation" in command:
            self.is_translating = False
            print("Translation stopped.")
        elif "enable ai" in command:
            self.llm_enabled = True
            self._speak("AI mode activated")
        elif "stop ai" in command:
            self.llm_enabled = False
            self._speak("AI mode deactivated")
        elif self.llm_enabled:
            response = lm.complete(f"Q: {command}\nA (short):").split('.')[0]
            self._speak(response or "I don't know")

        elif any(x in command for x in ["schedule", "synta", "planner", "plan"]):
            self.run_synta_schedule_module()

        elif any(x in command for x in ["teleprompter", "teleprompt", "prompting", "prompt"]):
            self._speak("Launching the teleprompter module.")
            self.run_teleprompter_module()
        else:
            print("Command not recognized. Say 'Enable AI' for smart mode")

    def _speak(self, text):
        try:
            print(f"Responding: {text}")
            self.stt.convert_text_to_speech(text, "hi")
        except Exception as e:
            print(f"TTS Error: {e}")

    def start_translation(self):
        print("Translation started. Say 'stop translation' to end.")
        while self.is_translating:
            try:
                text = self.stt.convert_speech_to_text()
                if text == "STOP":
                    print("Stopping translation as per user command.")
                    self._speak("Translation stopped.")
                    self.is_translating = False
                    break

                if text:
                    print(f"You said: {text}")
                    translated = self.stt.translate_text(text, "en", "hi")
                    print(f"Translated: {translated}")
                    self._speak(translated)
            except Exception as e:
                print(f"Translation Error: {e}")
                self._speak("Translation error occurred")
                break

    def run_teleprompter_module(self):
        try:
            prompt = tele.listen_for_prompt()
            if not prompt:
                self._speak("Could not understand your prompt.")
                return

            self._speak("Generating your script. Please wait.")
            script = tele.generate_script(prompt)
            if "[Error]" in script:
                self._speak("Failed to generate script.")
                return

            title = f"script_{int(time.time())}"
            tele.save_script_to_file(title, script)
            loaded_script = tele.load_script_from_file(title)

            if loaded_script:
                self._speak("Running teleprompter now.")
                tele.run_teleprompter(loaded_script)
            else:
                self._speak("Could not load the script.")

        except Exception as e:
            print(f"Teleprompter module error: {e}")
            self._speak("An error occurred while running the teleprompter.")
    def run_synta_schedule_module(self):
        try:
            self._speak("Generating your schedule. Please wait.")
            self.synta.regex_clean()
            self.synta.display()
            self._speak("Your schedule is ready.")
        except Exception as e:
            print(f"Synta module error: {e}")
            self._speak("An error occurred while generating your schedule.")


    def listen_for_command(self):
        try:
            with sr.Microphone() as source:
                print("\nListening... (say 'Enable AI' for help)")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=5)
                command = self.recognizer.recognize_google(audio)
                print(f"Heard: {command}")
                return command
        except sr.UnknownValueError:
            print("Couldn't understand audio")
            return ""
        except sr.WaitTimeoutError:
            print("Listening timeout")
            return ""
        except Exception as e:
            print(f"Listening Error: {e}")
            return ""

    def listen_and_execute(self):
        # Voice authentication handled externally
        threading.Thread(target=lambda: ft.app(target=flet_main), daemon=True).start()

        command = self.listen_for_command()
        if command:
            self.process_command(command)
        else:
            self._speak("No valid command detected. Exiting now.")

        print("Command processed. Shutting down.")


if __name__ == "__main__":
    print("Initializing Voice Assistant with Dashboard...")
    assistant = CentralAISystem()
    assistant.listen_and_execute()
