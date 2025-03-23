import numpy as np


def preprocess_audio(audio, target_sr=16000, input_sr=None):
    """Preprocess audio for ASR"""
    # If audio is not numpy array, convert it
    if not isinstance(audio, np.ndarray):
        audio = np.array(audio)

    # Convert to mono if needed
    if len(audio.shape) > 1:
        audio = audio.mean(axis=1)

    # TODO: Add resampling if input_sr is provided and different from target_sr

    # Normalize audio
    if np.abs(audio).max() > 1.0:
        audio = audio / np.abs(audio).max()

    return audio


def detect_silence(audio, threshold=0.01, window_size=1024):
    """Detect silence in audio"""
    # Calculate energy in windows
    energy = []
    for i in range(0, len(audio), window_size):
        window = audio[i:i + window_size]
        if len(window) == window_size:  # Only process full windows
            energy.append(np.sqrt(np.mean(window ** 2)))

    # Determine which windows are silent
    is_silent = [e < threshold for e in energy]

    return is_silent


def trim_silence(audio, threshold=0.01, window_size=1024):
    """Trim silence from the beginning and end of audio"""
    is_silent = detect_silence(audio, threshold, window_size)

    if all(is_silent):  # All silence
        return np.zeros(0, dtype=audio.dtype)

    # Find first non-silent window
    start = 0
    for i, silent in enumerate(is_silent):
        if not silent:
            start = i
            break

    # Find last non-silent window
    end = len(is_silent) - 1
    for i in range(len(is_silent) - 1, -1, -1):
        if not is_silent[i]:
            end = i
            break

    # Convert window indices to sample indices
    start_sample = start * window_size
    end_sample = min((end + 1) * window_size, len(audio))

    return audio[start_sample:end_sample]