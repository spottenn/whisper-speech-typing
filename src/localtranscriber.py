import threading

from faster_whisper import WhisperModel
from .transcriber import Transcriber
from .whisperqueue import WhisperQueue
import numpy as np


class LocalTranscriber(Transcriber):
    def __init__(self, model_size, compute_type, language, device, message_queue: WhisperQueue = None):
        self.model_size = model_size
        self.compute_type = compute_type
        self.language = language
        self.device = device
        self.message_queue = message_queue
        self.model = None
        self.start_lock = threading.Lock()
        threading.Thread(target=self.start).start()

    def transcribe_audio(self, audio):
        if self.model is None:
            self.start()
        segments, _ = self.model.transcribe(audio, vad_filter=True, without_timestamps=True, language=self.language)
        segments_list = list(segments)
        if len(segments_list) != 0:
            full_transcription = "".join(segment.text for segment in segments_list)
            # Check if the last character is not a whitespace
            if full_transcription and not full_transcription[-1].isspace():
                full_transcription += ' '

            # Remove leading whitespace
            return full_transcription.lstrip()
        print("Error transcribing. Blank audio?")
        return ""



    # TODO: start and stop methods to release resources

    def set_backend(self, backend):
        pass
    def stop(self):
        self.model = None
        pass

    def start(self):
        with self.start_lock:
            print("Loading model...")
            if self.model is not None:
                return
            try:
                self.model = WhisperModel(self.model_size, compute_type=self.compute_type, device=self.device)
            except ValueError as e:
                print(e)
                print("Computation type not supported. Defaulting to float32")
                self.compute_type = "float32"
                self.model = WhisperModel(self.model_size, compute_type=self.compute_type, device=self.device)
            # Warm up the model
            print("Starting model...")
            silent_audio = np.zeros(160, dtype=np.float32)
            segments, _ = self.model.transcribe(silent_audio, vad_filter=False, without_timestamps=True, language=self.language)
            list(segments)
            print("Model ready.")