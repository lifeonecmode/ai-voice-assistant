import os

# API Keys
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "AIzaSyBlVNruum0c5oHrHj3F7x0AVT4qexTD0sE")

# Audio settings
SAMPLE_RATE = 16000
CHANNELS = 1
CHUNK_SIZE = 1024
FORMAT = "int16"  # Format for PyAudio

# ASR model settings
ASR_MODEL = "espnet/librispeech_asr_train_asr_conformer6_n_fft512_hop_length256_raw_en_bpe5000_sp"

# TTS model settings
TTS_MODEL = "espnet/ljspeech_tts_train_transformer_raw_phn_tacotron_g2p_en_no_space_train.loss.ave"

# Dialogue settings
MODEL_NAME = "gemini-2.0-flash"
SYSTEM_PROMPT = """
You are a helpful, intelligent assistant. 
Be concise, friendly, and helpful in your responses.
"""