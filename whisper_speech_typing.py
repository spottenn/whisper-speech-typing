import pyaudio
import numpy as np
import keyboard
import pyautogui
from faster_whisper import WhisperModel
import threading
import time
import argparse
import wave
import io
import collections

class RealTimeTranscriber:
    def __init__(self, model_size, device, compute_type, language, hotkey, type_hotkey, buffer):
        self.p = pyaudio.PyAudio()
        self.frames = []
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.language = language
        self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        self.hotkey = hotkey
        self.is_recording = False
        self.lock = threading.Lock()
        self.type_hotkey = type_hotkey
        self.transcription = ""
        self.buffer = buffer
        self.circular_buffer = collections.deque(maxlen=16)
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=16000,
                                  input=True,
                                  frames_per_buffer=1024,
                                  stream_callback=self.audio_callback)
        if self.buffer:
            self.stream.start_stream()

    def audio_callback(self, in_data, frame_count, time_info, status):
        data = np.frombuffer(in_data, dtype=np.int16)
        with self.lock:
            if self.is_recording:
                self.frames.append(data)
            else:
                self.circular_buffer.append(data)
        return (None, pyaudio.paContinue)

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
        while self.is_recording:
            time.sleep(0.1)


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

        # Calculate the file size in MB and print
        file_size_mb = len(audio_data) / (1024 * 1024)  # 1 MB = 1024 KB = 1024 * 1024 Bytes
        print(f"Audio size: {file_size_mb:.2f} MB")
        return audio_buffer

    def transcribe_audio(self, audio, language):
        segments, _ = self.model.transcribe(audio, without_timestamps=True, language=language)
        segments_list = list(segments)

        if len(segments_list) != 0:
            full_transcription = " ".join(segment.text for segment in segments_list)
            return full_transcription
        print("Error transcribing. Blank audio?")
        return ""

    def post_process(self, input_string):
        return input_string.lstrip()

    def type_text(self, text):
        if text is None:
            print("Empty text.")
            return
        processed_text = self.post_process(text)
        pyautogui.write(processed_text)

    def process_hotkeys(self):
        if keyboard.is_pressed(self.hotkey):
            print("Capturing audio... Release F4 to stop.")
            threading.Thread(target=self.start_audio_capture).start()
            while keyboard.is_pressed(self.hotkey):
                time.sleep(0.1)
            audio = self.stop_audio_capture()
            print("Transcribing audio...")
            self.transcription = self.transcribe_audio(audio, self.language)
            print("Typing out transcription...")
            self.type_text(self.transcription)
            print("Done.")
        elif keyboard.is_pressed(self.type_hotkey):
            print("Typing out transcription...")
            self.type_text(self.transcription)
            time.sleep(0.2)  # To prevent the CPU usage from spiking if someone holds the hotkey.
            print("Done.")
        return True  # Continue running

    def main(self):
        print(f"Press and hold {self.hotkey} and start speaking. Release to type.")
        print(f"Press {self.type_hotkey} to retype the most recent speech. Press Ctrl + C to exit")
        try:
            while self.process_hotkeys():
                time.sleep(0.05)
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Stopping transcriber...")
            self.stop_audio_capture()
            self.stream.close()
            self.p.terminate()
            print("Transcriber stopped.")




if __name__ == "__main__":
    try:
        parser = argparse.ArgumentParser(description='Voice typing script.')
        parser.add_argument('--model_size', type=str, default='large-v2', help='Size of the Whisper model')
        parser.add_argument('--device', type=str, default='cuda', help='Device to run the Whisper model on')
        parser.add_argument('--compute_type', type=str, default='float16', help='Compute datatype for the Whisper model')
        parser.add_argument('--language', type=str, default='en', help='Compute datatype for the Whisper model')
        parser.add_argument('--hotkey', type=str, default='f4', help='Hotkey to start/stop audio capture')
        parser.add_argument('--type_hotkey', type=str, default='f2', help='Hotkey to just type the transcription')
        parser.add_argument('--buffer', action='store_true', default=False, help='Buffer one second of audio before hotkey is pressed')
        args = parser.parse_args()
        transcriber = RealTimeTranscriber(model_size=args.model_size, device=args.device,
                                          compute_type=args.compute_type, language=args.language, hotkey=args.hotkey,
                                          type_hotkey=args.type_hotkey, buffer=args.buffer)
        transcriber.main()
    except Exception as e:
        print(e)
