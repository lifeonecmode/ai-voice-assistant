import numpy as np
from espnet2.bin.tts_inference import Text2Speech
import logging


class SpeechSynthesizer:
    def __init__(self, model_name):
        """Initialize the speech synthesizer with a pre-trained model"""
        try:
            self.model = Text2Speech.from_pretrained(model_name)
            self.sample_rate = self.model.fs
            logging.info(f"Loaded TTS model: {model_name}")
        except Exception as e:
            logging.error(f"Failed to load TTS model: {e}")
            raise

    def synthesize(self, text):
        """Convert text to speech"""
        try:
            if not text:
                return np.zeros(0, dtype=np.float32)

            # Generate speech
            with_duration = self.model(text)
            wav = with_duration["wav"]

            # Convert to numpy array if it's a tensor
            if hasattr(wav, "numpy"):
                wav = wav.numpy()

            return wav
        except Exception as e:
            logging.error(f"Speech synthesis error: {e}")
            return np.zeros(0, dtype=np.float32)

    def get_sample_rate(self):
        """Get the sample rate of the model"""
        return self.sample_rate