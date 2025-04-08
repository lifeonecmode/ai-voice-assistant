#!/usr/bin/env python3
import os
import sys
import time
import logging
import subprocess
import tempfile
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)


def capture_audio_macos():
    """Capture audio using macOS native tools"""
    try:
        # Create a temporary file
        fd, temp_path = tempfile.mkstemp(suffix='.aiff')
        os.close(fd)

        # Use macOS's built-in recording tool
        print("Listening... (speak now for up to 7 seconds)")
        subprocess.run(["afplay", "/System/Library/Sounds/Submarine.aiff"])  # Play a sound to indicate recording start

        # Record audio (7 seconds)
        subprocess.run([
            "rec", "-q",  # rec is part of sox, but we use specific settings
            temp_path,  # output file
            "rate", "16k",  # 16kHz sample rate (good for speech)
            "channels", "1",  # mono
            "trim", "0", "7"  # record for 7 seconds
        ], check=True)

        print("Processing audio...")

        # Convert speech to text using Google's API directly
        # This bypasses potential local format issues
        recognizer = sr.Recognizer()
        with sr.AudioFile(temp_path) as source:
            audio_data = recognizer.record(source)
            text = recognizer.recognize_google(audio_data)

        # Clean up the temporary file
        os.unlink(temp_path)
        return text

    except subprocess.CalledProcessError as e:
        logging.error(f"Error running audio recording command: {e}")
        return None
    except sr.UnknownValueError:
        logging.error("Speech recognition could not understand audio")
        return None
    except sr.RequestError as e:
        logging.error(f"Could not request results from speech recognition service: {e}")
        return None
    except Exception as e:
        logging.error(f"Error capturing audio: {e}")
        if os.path.exists(temp_path):
            os.unlink(temp_path)
        return None


def main():
    # Check for API key
    api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyBlVNruum0c5oHrHj3F7x0AVT4qexTD0sE")
    if not api_key:
        print("Please set the GEMINI_API_KEY environment variable and try again.")
        return

    # Initialize Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-2.0-flash")

    # Initialize speech synthesizer
    engine = pyttsx3.init()

    # Make voice slower and more conversational
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 50)  # Slow down the speech rate

    voices = engine.getProperty('voices')
    # Choose a more natural-sounding voice if available
    for voice in voices:
        if "female" in voice.name.lower():  # Or any preference you have
            engine.setProperty('voice', voice.id)
            break

    # Increase the volume slightly
    volume = engine.getProperty('volume')
    engine.setProperty('volume', min(volume * 1.25, 1.0))

    print("\n==== Enhanced Voice Conversational AI System ====")
    print("Speak when prompted. Press Ctrl+C at any time to exit.")

    # Improved system prompt for more conversational tone
    system_prompt = """
    You are a friendly, conversational assistant named Alex. Speak in a natural, warm tone as if 
    talking to a friend. Use occasional conversational markers like "you know", "well", and 
    respond to emotional cues. Keep your responses concise but natural. Ask follow-up questions 
    when appropriate to maintain the conversation flow. Avoid sounding robotic or overly formal.
    """

    # Conversation history for context
    conversation_history = []

    try:
        # Start with a greeting
        greeting = "Hi there! I'm Alex, your AI assistant. How can I help you today?"
        print(f"AI: \"{greeting}\"")
        engine.say(greeting)
        engine.runAndWait()

        # Add greeting to history
        conversation_history.append({"role": "model", "parts": [greeting]})

        while True:
            print("\n> Your turn (speak now)...")

            # Capture audio using macOS native tools
            user_text = capture_audio_macos()

            if not user_text:
                print("Could not understand audio. Please try again.")
                engine.say("I couldn't understand that. Could you please try again?")
                engine.runAndWait()
                continue

            print(f"You said: \"{user_text}\"")

            if user_text.lower() in ["exit", "quit", "goodbye", "bye"]:
                print("Ending conversation...")
                engine.say("Goodbye! It was nice talking with you.")
                engine.runAndWait()
                break

            # Add pauses to seem more natural
            time.sleep(0.5)

            # Add to conversation history
            conversation_history.append({"role": "user", "parts": [user_text]})

            # Generate AI response
            print("Thinking...")
            time.sleep(1)  # Slight pause to seem more natural

            if len(conversation_history) == 2:  # Count includes the greeting
                # First user message, create a new chat
                chat = model.start_chat(history=[])
                # Set system prompt
                chat.send_message(system_prompt)
            else:
                # Format history for Gemini
                formatted_history = []
                for entry in conversation_history[:-1]:  # Exclude the current user message
                    formatted_history.append({
                        "role": entry["role"],
                        "parts": [entry["parts"][0]]
                    })
                chat = model.start_chat(history=formatted_history)

            response = chat.send_message(user_text)
            ai_text = response.text

            # Add AI response to history
            conversation_history.append({"role": "model", "parts": [ai_text]})

            # Keep history manageable
            if len(conversation_history) > 20:
                conversation_history = conversation_history[-20:]

            print(f"AI: \"{ai_text}\"")

            # Convert response to speech with natural pauses between sentences
            print("Speaking...")
            sentences = ai_text.split(". ")
            for sentence in sentences:
                if sentence.strip():
                    engine.say(sentence.strip())
                    engine.runAndWait()
                    time.sleep(0.3)  # Small pause between sentences

            # Optional: Save the conversation
            with open("conversation_log.txt", "a") as f:
                f.write(f"User: {user_text}\n")
                f.write(f"AI: {ai_text}\n\n")

    except KeyboardInterrupt:
        print("\nConversation ended by user.")
        engine.say("Goodbye! It was nice talking with you.")
        engine.runAndWait()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        print(f"An error occurred: {e}")
        engine.say("I've encountered a problem. Let's restart our conversation.")
        engine.runAndWait()
    finally:
        print("Thank you for using the conversational AI system.")


if __name__ == "__main__":
    main()