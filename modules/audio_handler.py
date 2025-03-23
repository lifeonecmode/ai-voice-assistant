import numpy as np
import sounddevice as sd
import queue
import threading
import time
import logging
import pyaudio


class AudioHandler:
    def __init__(self, sample_rate=16000, channels=1, chunk_size=1024, format='int16'):
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = format

        # Convert format string to PyAudio format
        format_map = {
            'int16': pyaudio.paInt16,
            'int32': pyaudio.paInt32,
            'float32': pyaudio.paFloat32
        }
        self.pa_format = format_map.get(format, pyaudio.paInt16)

        # Initialize PyAudio
        self.p = pyaudio.PyAudio()

        # Recording variables
        self.buffer_queue = queue.Queue()
        self.is_recording = False
        self.recording = []

        # Auto-stop settings
        self.silence_threshold = 0.01
        self.silence_frames = 0
        self.max_silence_frames = 30  # 30 chunks of silence to auto-stop

    def record_callback(self, in_data, frame_count, time_info, status):
        """Callback for recording"""
        if status:
            logging.warning(f"Recording status: {status}")
        self.buffer_queue.put(in_data)
        return (None, pyaudio.paContinue)

    def record(self, duration=None, auto_stop=True):
        """Record audio from microphone

        Args:
            duration: Maximum recording duration in seconds (None for unlimited)
            auto_stop: Whether to automatically stop recording after silence

        Returns:
            Audio data as numpy array
        """
        self.is_recording = True
        self.recording = []
        self.silence_frames = 0

        # Open recording stream
        stream = self.p.open(
            format=self.pa_format,
            channels=self.channels,
            rate=self.sample_rate,
            input=True,
            frames_per_buffer=self.chunk_size,
            stream_callback=self.record_callback
        )

        stream.start_stream()
        logging.info("Recording started...")
        print("Listening... (speak now)")

        start_time = time.time()
        try:
            while self.is_recording:
                # Check if we've hit the duration limit
                if duration and (time.time() - start_time) > duration:
                    self.is_recording = False
                    break

                # Process recorded data
                if not self.buffer_queue.empty():
                    data = self.buffer_queue.get()
                    self.recording.append(data)

                    # Check for silence to auto-stop
                    if auto_stop:
                        # Convert bytes to numpy array
                        if self.pa_format == pyaudio.paInt16:
                            data_np = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32767.0
                        elif self.pa_format == pyaudio.paInt32:
                            data_np = np.frombuffer(data, dtype=np.int32).astype(np.float32) / 2147483647.0
                        elif self.pa_format == pyaudio.paFloat32:
                            data_np = np.frombuffer(data, dtype=np.float32)

                        # Calculate energy
                        energy = np.sqrt(np.mean(data_np ** 2))
                        is_speech = energy > self.silence_threshold

                        if not is_speech:
                            self.silence_frames += 1
                        else:
                            self.silence_frames = 0

                        # Stop if silence threshold is exceeded and we have some speech
                        if self.silence_frames > self.max_silence_frames and len(self.recording) > 5:
                            self.is_recording = False
                else:
                    time.sleep(0.01)
        finally:
            stream.stop_stream()
            stream.close()

        print("Recording finished.")

        # Convert recorded data to numpy array
        if not self.recording:
            return np.zeros(0, dtype=np.float32)

        # Concatenate all audio chunks
        if self.pa_format == pyaudio.paInt16:
            audio_data = np.frombuffer(b''.join(self.recording), dtype=np.int16).astype(np.float32) / 32767.0
        elif self.pa_format == pyaudio.paInt32:
            audio_data = np.frombuffer(b''.join(self.recording), dtype=np.int32).astype(np.float32) / 2147483647.0
        elif self.pa_format == pyaudio.paFloat32:
            audio_data = np.frombuffer(b''.join(self.recording), dtype=np.float32)

        return audio_data

    def play(self, audio_data):
        """Play audio data"""
        # If audio data is empty, do nothing
        if len(audio_data) == 0:
            return

        # Ensure audio is in float32 format
        if audio_data.dtype != np.float32:
            audio_data = audio_data.astype(np.float32)

        # Ensure audio is in the range [-1, 1]
        if np.abs(audio_data).max() > 1.0:
            audio_data = audio_data / np.abs(audio_data).max()

        # Play the audio
        sd.play(audio_data, self.sample_rate)
        sd.wait()

    def __del__(self):
        """Clean up resources"""
        if hasattr(self, 'p'):
            self.p.terminate()