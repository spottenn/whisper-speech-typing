import pyaudio
import numpy as np
import keyboard
import pyautogui
from faster_whisper import WhisperModel
import threading
import time
import argparse


class RealTimeTranscriber:
    def __init__(self, model_size, device, compute_type, hotkey):
        self.p = pyaudio.PyAudio()
        self.stream = None
        self.frames = []
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        self.hotkey = hotkey
        self.is_recording = False
        self.lock = threading.Lock()

    def start_audio_capture(self):
        with self.lock:
            self.frames = []
            self.is_recording = True
        self.stream = self.p.open(format=pyaudio.paInt16,
                                  channels=1,
                                  rate=16000,
                                  input=True,
                                  frames_per_buffer=1024)
        while self.is_recording:
            data = self.stream.read(1024)
            with self.lock:
                self.frames.append(np.frombuffer(data, dtype=np.int16))
        self.stream.stop_stream()
        self.stream.close()

    def stop_audio_capture(self):
        with self.lock:
            self.is_recording = False
        audio_data = np.concatenate(self.frames)
        return audio_data

    def transcribe_audio(self, audio):
        segments, _ = self.model.transcribe(audio, without_timestamps=True)
        segments_list = list(segments)

        if len(segments_list) != 0:
            return segments_list[0].text
        print("Error transcribing. Blank audio?")
        return

    def type_text(self, text):
        pyautogui.typewrite(text)

    def main(self):
        print(f"Press and hold {self.hotkey} to start audio capture. Release {self.hotkey} to transcribe and type.")
        while True:
            if keyboard.is_pressed(self.hotkey):
                print("Capturing audio... Release F4 to stop.")
                threading.Thread(target=self.start_audio_capture).start()
                while keyboard.is_pressed(self.hotkey):
                    time.sleep(0.1)
                audio = self.stop_audio_capture()
                print("Transcribing audio...")
                transcription = self.transcribe_audio(audio)
                print("Typing out transcription...")
                self.type_text(transcription)
                print("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Real-Time Speech-to-Text Transcription')
    parser.add_argument('--model_size', type=str, default='large-v2', help='Size of the Whisper model')
    parser.add_argument('--device', type=str, default='cuda', help='Device to run the Whisper model on')
    parser.add_argument('--compute_type', type=str, default='float16', help='Compute datatype for the Whisper model')
    parser.add_argument('--hotkey', type=str, default='f4', help='Hotkey to start/stop audio capture')

    args = parser.parse_args()

    transcriber = RealTimeTranscriber(model_size=args.model_size, device=args.device, compute_type=args.compute_type,
                                      hotkey=args.hotkey)
    transcriber.main()
