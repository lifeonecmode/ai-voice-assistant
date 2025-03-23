import google.generativeai as genai
import json
import logging


class DialogueManager:
    def __init__(self, api_key, model_name="gemini-1.5-flash", system_prompt=None):
        """Initialize dialogue manager with Gemini API"""
        self.api_key = api_key
        genai.configure(api_key=api_key)

        try:
            self.model = genai.GenerativeModel(model_name)
            logging.info(f"Initialized Gemini model: {model_name}")
        except Exception as e:
            logging.error(f"Failed to initialize Gemini model: {e}")
            raise

        self.system_prompt = system_prompt or """
        You are a helpful, intelligent assistant.
        Be concise, friendly, and helpful in your responses.
        """

        # Conversation history
        self.conversation_history = []

    def get_response(self, user_text):
        """Generate a response to user input"""
        if not user_text:
            return "I didn't catch that. Could you please repeat?"

        try:
            # Add user input to history
            self.conversation_history.append({"role": "user", "parts": [user_text]})

            # Start chat with the system prompt
            if len(self.conversation_history) == 1:
                chat = self.model.start_chat(history=[])
                chat.send_message(self.system_prompt)
            else:
                # Format history for Gemini
                formatted_history = []
                for entry in self.conversation_history[:-1]:  # Exclude the current user message
                    formatted_history.append({
                        "role": entry["role"],
                        "parts": [entry["parts"][0]]
                    })
                chat = self.model.start_chat(history=formatted_history)

            # Get response from Gemini
            response = chat.send_message(user_text)
            response_text = response.text

            # Add AI response to history
            self.conversation_history.append({"role": "model", "parts": [response_text]})

            # Keep history manageable (last 10 exchanges)
            if len(self.conversation_history) > 20:
                self.conversation_history = self.conversation_history[-20:]

            return response_text
        except Exception as e:
            logging.error(f"Dialogue error: {e}")
            return "I'm having trouble processing that. Could you try again?"