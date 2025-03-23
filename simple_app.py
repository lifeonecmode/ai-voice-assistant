
import os
import time
import google.generativeai as genai
import pyttsx3


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

    print("\n==== Text-Based Conversational AI System ====")
    print("Type your messages. Type 'exit' to quit.")

    # Conversation history for context
    conversation_history = []

    try:
        while True:
            # Get user input
            user_text = input("\n> You: ")

            if user_text.lower() == 'exit':
                break

            # Add to conversation history
            conversation_history.append({"role": "user", "parts": [user_text]})

            # Generate AI response
            print("Thinking...")

            if len(conversation_history) == 1:
                # First message, create a new chat
                chat = model.start_chat(history=[])
                # Set system prompt
                chat.send_message(
                    "You are a helpful, intelligent assistant. Be concise, friendly, and helpful in your responses.")
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

            print(f"\n> AI: {ai_text}")

            # Convert response to speech
            print("Speaking...")
            engine.say(ai_text)
            engine.runAndWait()

            # Optional: Save the conversation
            with open("conversation_log.txt", "a") as f:
                f.write(f"User: {user_text}\n")
                f.write(f"AI: {ai_text}\n\n")

    except KeyboardInterrupt:
        print("\nConversation ended by user.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Thank you for using the conversational AI system.")


if __name__ == "__main__":
    main()
