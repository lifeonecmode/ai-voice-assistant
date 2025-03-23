import numpy as np
from espnet2.bin.asr_inference import Speech2Text
import logging


class SpeechRecognizer:
    def __init__(self, model_name):
        """Initialize the speech recognizer with a pre-trained model"""
        try:
            self.model = Speech2Text.from_pretrained(model_name)
            logging.info(f"Loaded ASR model: {model_name}")
        except Exception as e:
            logging.error(f"Failed to load ASR model: {e}")
            raise

    def transcribe(self, audio, sample_rate=16000):
        """Convert speech to text"""
        try:
            # Ensure audio is in the correct format
            if audio.dtype != np.float32:
                audio = audio.astype(np.float32)

            # If audio is stereo, convert to mono
            if len(audio.shape) > 1:
                audio = audio.mean(axis=1)

            # Normalize audio
            if np.abs(audio).max() > 1.0:
                audio = audio / np.abs(audio).max()

            # Recognize speech
            nbests = self.model(audio)
            text, *_ = nbests[0]

            return {"text": text, "confidence": 1.0}
        except Exception as e:
            logging.error(f"Transcription error: {e}")
            return {"text": "", "confidence": 0.0}