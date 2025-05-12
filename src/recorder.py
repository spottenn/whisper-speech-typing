import pyaudio
import numpy as np
import threading
import io
import wave
import collections
import time
from whisperqueue import WhisperQueue


class Recorder:
    def __init__(self, buffer, message_queue: WhisperQueue = None):
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.buffer = buffer
        self.is_recording = False
        self.lock = threading.Lock()
        self.circular_buffer = collections.deque(maxlen=8)
        self.message_queue = message_queue

        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=16000,
                                  input=True,
                                  frames_per_buffer=1000,
                                  stream_callback=self.audio_callback,
                                  start=False)
        if self.buffer:
            self.stream.start_stream()

    def audio_callback(self, in_data, frame_count, time_info, status):
        data = np.frombuffer(in_data, dtype=np.int16)
        with self.lock:
            if self.is_recording:
                self.frames.append(data)
            else:
                self.circular_buffer.append(data)
        return None, pyaudio.paContinue

    def start_audio_capture(self):
        with self.lock:
            if self.buffer:
                self.frames = []
                self.frames.extend(self.circular_buffer)
                self.circular_buffer.clear()
            else:
                self.frames = []
                self.stream.start_stream()
            self.is_recording = True


    def stop_audio_capture(self):
        with self.lock:
            self.is_recording = False
        if not self.buffer:
            self.stream.stop_stream()
        audio_data = b''.join(self.frames)
        audio_buffer = io.BytesIO(audio_data)

        wave_file = wave.open(audio_buffer, 'wb')
        wave_file.setnchannels(1)
        wave_file.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wave_file.setframerate(16000)
        wave_file.writeframes(audio_data)
        wave_file.close()

        audio_buffer.seek(0)  # Move the cursor to the start of the BytesIO buffer
        return audio_buffer
