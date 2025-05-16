# Import required libraries for I2C communication, audio processing, and voice recognition
import time
import board
import busio
import subprocess
from adafruit_cap1xxx.cap1203 import CAP1203
from speech_recognition import Recognizer, Microphone
from resemblyzer import VoiceEncoder, preprocess_wav
import numpy as np

# Initialize I2C communication and capacitive touch sensor
i2c = busio.I2C(board.SCL, board.SDA)
cap = CAP1203(i2c)
recognizer = Recognizer()

# Initialize authentication state variables
authenticated = False
last_active_time = 0
LOCK_TIMEOUT = 20 * 60  # 20 minutes in seconds

def voice_authenticate():
    """Function to perform voice-based authentication by comparing voice samples"""
    print("Please say your passphrase now.")
    try:
        # Record audio from microphone
        with Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)  # Adjust for background noise
            audio = recognizer.listen(source)
            # Save the recorded audio attempt
            with open("attempt.wav", "wb") as f:
                f.write(audio.get_wav_data())

        # Initialize voice encoder and process both stored and attempt WAV files
        encoder = VoiceEncoder()
        stored_wav = preprocess_wav("reference.wav")  # Load stored voice reference
        attempt_wav = preprocess_wav("attempt.wav")   # Load current voice attempt

        # Create voice embeddings for comparison
        stored_embed = encoder.embed_utterance(stored_wav)
        attempt_embed = encoder.embed_utterance(attempt_wav)

        # Calculate similarity score using cosine similarity
        similarity = np.dot(stored_embed, attempt_embed) / (
            np.linalg.norm(stored_embed) * np.linalg.norm(attempt_embed)
        )
        print(f"Voice similarity score: {similarity:.2f}")
        return similarity > 0.3  # Return True if similarity exceeds threshold

    except Exception as e:
        print(f"Voice authentication error: {e}")
        return False

print("Touch slider is ready...")

# Main program loop
while True:
    # Check for session timeout and auto-lock if inactive
    if authenticated and (time.time() - last_active_time > LOCK_TIMEOUT):
        print("Session timed out due to inactivity. Re-authentication required.")
        authenticated = False

    # Handle touch pad input (C2)
    if cap[2].value:  # When touch pad 2 is activated
        print("C2 touched!")
        if not authenticated:
            # Perform voice authentication if not already authenticated
            print("Starting voice authentication...")
            if voice_authenticate():
                print("Access granted.")
                authenticated = True
                last_active_time = time.time()
                # Launch the main AI system upon successful authentication
                subprocess.Popen(["python3", "/home/pi/Central_AI_System.py"])
            else:
                print("Access denied.")
        else:
            # Update activity timestamp if already authenticated
            print("Already authenticated. Updating activity timestamp.")
            last_active_time = time.time()

        time.sleep(2)  # Delay to prevent multiple touch triggers
    time.sleep(0.1)  # Small delay in main loop for CPU efficiency
