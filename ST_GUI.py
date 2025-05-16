import pygame
import speech_recognition as sr
from gtts import gTTS
from googletrans import Translator
import tempfile
import os
import time
import sys

# Initialize pygame only if it hasn't been initialized
if not pygame.get_init():
    pygame.init()
    pygame.font.init()
    pygame.mixer.init()

# Set up Pygame window
WIDTH, HEIGHT = 800, 480
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Smart Glass Translator Test")

# Colors for the interface
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)

# Translator for translating English to Hindi
translator = Translator()

# Load Hindi font (replace with actual font path on your system)
font_path = "C:\\Users\\hp\\Downloads\\Noto_Sans_Devanagari\\static\\NotoSansDevanagari-Regular.ttf"
try:
    font = pygame.font.Font(font_path, 36)
except:
    font = pygame.font.Font(None, 36)  # Default font if the custom one fails

# Function to recognize speech and return the recognized text
def recognize_speech():
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    with mic as source:
        print("Say something in English...")
        recognizer.adjust_for_ambient_noise(source)
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
        except sr.WaitTimeoutError:
            print("No speech detected within timeout period.")
            return None
    
    try:
        print("Recognizing...")
        recognized_text = recognizer.recognize_google(audio)
        print(f"Recognized Text: {recognized_text}")
        return recognized_text
    except sr.UnknownValueError:
        print("Sorry, I could not understand the audio.")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None
    except Exception as e:
        print(f"An error occurred during speech recognition: {e}")
        return None

# Function to translate text from English to Hindi
def translate_to_hindi(text):
    print("Translating to Hindi...")
    hindi_translation = translator.translate(text, src='en', dest='hi').text
    print(f"Translated Hindi Text: {hindi_translation}")
    return hindi_translation

# Function to speak the translated text
def speak_translation(hindi_text):
    tts = gTTS(hindi_text, lang='hi')

    # Create a temporary audio file to save the speech
    with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as temp_audio_file:
        temp_audio_file.close()  # Close the file so gTTS can write to it
        tts.save(temp_audio_file.name)  # Save the speech to the temp file
        
        # Ensure the file is properly saved before proceeding
        if os.path.exists(temp_audio_file.name):

            # Initialize pygame mixer and load the audio file
            pygame.mixer.music.load(temp_audio_file.name)
            pygame.mixer.music.play()  # Play the speech
            
            # Wait until the audio finishes playing
            while pygame.mixer.music.get_busy():  # Check if the audio is still playing
                pygame.time.Clock().tick(10)  # Wait for the audio to finish (check every 10ms)
            
            # Explicitly stop the music and unload it after playing
            pygame.mixer.music.stop()  # Stop the music explicitly
            pygame.mixer.music.unload()  # Unload the music to release the file
            
            # Attempt to delete the temporary audio file
            try:
                os.remove(temp_audio_file.name)  # Delete the temporary audio file after playing
            except PermissionError:
                pass  # Ignore the error silently if the file is still in use

# Function to display translated text on screen (with wrapping)
def display_text_on_screen(text):
    screen.fill(BLACK)
    
    # Break the text into multiple lines if it's too long
    lines = []
    words = text.split(' ')
    current_line = ""
    
    for word in words:
        test_line = current_line + word + " "
        test_surface = font.render(test_line, True, GREEN)
        if test_surface.get_width() > WIDTH - 40:  # Check if line exceeds screen width
            lines.append(current_line)
            current_line = word + " "
        else:
            current_line = test_line
    
    if current_line:
        lines.append(current_line)

    # Render each line
    y_offset = HEIGHT // 2 - (len(lines) * 18)  # Adjust so lines are vertically centered
    for line in lines:
        text_surface = font.render(line, True, GREEN)
        screen.blit(text_surface, (20, y_offset))
        y_offset += 36  # Space between lines
    
    pygame.display.update()

# Main loop for the program
def main():
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Recognize speech, translate, and speak the translation
        english_text = recognize_speech()
        if english_text:
            if 'stop translation' in english_text.lower():  # Stop translation command
                print("Stopping translation.")
                running = False
            else:
                hindi_text = translate_to_hindi(english_text)
                display_text_on_screen(hindi_text)  # Show the translated text on the screen
                speak_translation(hindi_text)  # Speak the translation

        pygame.time.Clock().tick(10)  # Control the frame rate (10 FPS)

    pygame.quit()

if __name__ == "__main__":
    main()
