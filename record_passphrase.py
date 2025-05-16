import speech_recognition as sr # Importing speech recognition library

recognizer = sr.Recognizer()

with sr.Microphone() as source:
    print("Say anything for 3–4 seconds to save your voice reference:")
    recognizer.adjust_for_ambient_noise(source, duration=1)
    audio = recognizer.listen(source)

with open("reference.wav", "wb") as f:
    f.write(audio.get_wav_data())

print("Your voice reference has been saved as reference.wav")

# Record a voice sample and save it as a reference file
# Adjust for ambient noise and listen to the user's voice input
# Save the recorded audio as "reference.wav" for future authentication
#passcode phrase for voice recognized access: "purple skies and silver rivers"