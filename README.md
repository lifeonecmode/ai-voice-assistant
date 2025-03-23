# AI Voice Assistant

A voice-based conversational AI assistant powered by Google's Gemini API. This application allows you to have natural, voice-based conversations with an AI assistant named Alex.

## Features

- **Voice input and output**: Speak to the assistant and receive spoken responses
- **Natural conversation flow**: Designed to feel more like talking to a person than a robot
- **Conversation memory**: The assistant remembers the context of your conversation
- **Conversation logging**: Saves your conversations to a text file for future reference
- **Customizable voice**: Adjustable speech rate and voice selection
- **Cross-platform support**: Works on macOS and Windows (with platform-specific setup)

## Requirements

- Python 3.8 or higher
- Google Gemini API key
- Platform-specific audio tools (see setup instructions)

## Installation

### 1. Clone the repository or download the code files

### 2. Install Python dependencies

```bash
pip install google-generativeai pyttsx3 SpeechRecognition
```

### 3. Get a Gemini API key

1. Visit [Google AI Studio](https://aistudio.google.com/)
2. Create an account or sign in
3. Generate an API key

### 4. Platform-specific setup

#### macOS Setup

For macOS, you'll need to install `sox`:

```bash
brew install sox
```

#### Windows Setup

For Windows, you'll need to install:

1. PyAudio (Windows has better PyAudio support than macOS):

```bash
pip install pyaudio
```

2. SpeechRecognition:

```bash
pip install SpeechRecognition
```

## Usage

### Set your API key

```bash
# macOS/Linux
export GEMINI_API_KEY="your_api_key_here"

# Windows
set GEMINI_API_KEY=your_api_key_here
```

### Run the application

```bash
python voice_app.py
```

For Windows users, use the Windows-specific version:

```bash
python windows_voice_app.py
```

## Windows-Specific Version

Windows users should use the modified version of the code that leverages PyAudio directly, as it works better on Windows systems. The included `windows_voice_app.py` file contains Windows-optimized code.

Key differences in the Windows version:
- Uses PyAudio directly for audio recording
- Adjusted audio parameters for Windows microphones
- Windows-compatible file path handling
- Option to use Windows native voices

## Customizing the Assistant

You can customize the assistant by modifying the following parameters:

- **Voice selection**: Change the voice by modifying the voice selection code
- **Speech rate**: Adjust how quickly the assistant speaks
- **Recording time**: Change how long the assistant listens for input
- **System prompt**: Modify the assistant's personality and behavior

## Troubleshooting

### macOS Issues

- If you encounter PyAudio installation issues, use the macOS-native version that uses `sox` instead
- Make sure your microphone permissions are enabled in System Preferences

### Windows Issues

- Check your microphone is set as the default recording device
- Ensure you've installed PyAudio correctly
- Try running the command prompt as Administrator if you encounter permission issues

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Google Gemini API for AI capabilities
- pyttsx3 for text-to-speech
- SpeechRecognition for speech recognition
- The open-source community for audio tools and libraries