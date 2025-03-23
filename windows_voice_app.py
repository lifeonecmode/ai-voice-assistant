#!/usr/bin/env python3
import os
import sys
import time
import logging
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)


def main():
    # Check for API key
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        print("Please set the GEMINI_API_KEY environment variable and try again.")
        print("Use: set GEMINI_API_KEY=your_api_key_here (on Windows)")
        return

    # Initialize Gemini
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel("gemini-1.5-flash")

    # Initialize speech recognizer
    recognizer = sr.Recognizer()

    # Initialize speech synthesizer
    engine = pyttsx3.init()

    # Make voice slower and more conversational
    rate = engine.getProperty('rate')
    engine.setProperty('rate', rate - 50)  # Slow down the speech rate

    # Get available voices
    voices = engine.getProperty('voices')

    # Show available voices
    print("\nAvailable voices:")
    for i, voice in enumerate(voices):
        print(f"{i}: {voice.name} ({voice.id})")

    # Let user choose a voice (default to first voice if input is invalid)
    try:
        voice_choice = input("Choose a voice number (or press Enter for default): ")
        if voice_choice.strip():
            voice_index = int(voice_choice)
            if 0 <= voice_index < len(voices):
                engine.setProperty('voice', voices[voice_index].id)
                print(f"Using voice: {voices[voice_index].name}")
            else:
                print("Invalid choice, using default voice")
        else:
            print("Using default voice")
    except ValueError:
        print("Invalid input, using default voice")

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

            # Record speech
            with sr.Microphone() as source:
                # Adjust for ambient noise before each recording
                print("Adjusting for ambient noise...")
                recognizer.adjust_for_ambient_noise(source, duration=1)

                print("Listening...")
                try:
                    # Wait for 7 seconds max for the user to speak
                    audio = recognizer.listen(source, timeout=7, phrase_time_limit=7)
                except sr.WaitTimeoutError:
                    print("No speech detected. Please try again.")
                    engine.say("I didn't hear anything. Could you please try again?")
                    engine.runAndWait()
                    continue

            try:
                # Convert speech to text
                print("Processing speech...")
                user_text = recognizer.recognize_google(audio)

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

                # Save the conversation to log file
                log_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "conversation_log.txt")
                with open(log_path, "a", encoding="utf-8") as f:
                    f.write(f"User: {user_text}\n")
                    f.write(f"AI: {ai_text}\n\n")

            except sr.UnknownValueError:
                print("Could not understand audio")
                engine.say("I'm sorry, I couldn't understand that. Could you please repeat?")
                engine.runAndWait()
            except sr.RequestError as e:
                print(f"Could not request results; {e}")
                engine.say("I'm having trouble connecting to my speech services. Let's try again.")
                engine.runAndWait()
            except Exception as e:
                logging.error(f"Error processing speech: {e}")
                print(f"An error occurred: {e}")
                engine.say("I encountered a problem. Let's try again.")
                engine.runAndWait()

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