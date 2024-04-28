from faster_whisper import WhisperModel
from transcriber import Transcriber
from whisperqueue import WhisperQueue
import numpy as np


class LocalTranscriber(Transcriber):
    def __init__(self, model_size, compute_type, language, device, message_queue: WhisperQueue = None):
        self.model_size = model_size
        self.compute_type = compute_type
        self.language = language
        self.device = device
        self.message_queue = message_queue
        try:
            self.model = WhisperModel(self.model_size, compute_type=self.compute_type, device=self.device)
        except ValueError as e:
            print(e)
            print("Computation type not supported. Defaulting to float32")
            self.compute_type = "float32"
            self.model = WhisperModel(self.model_size, compute_type=self.compute_type, device=self.device)


        silent_audio = np.zeros(160, dtype=np.float32)

        segments, _ = self.model.transcribe(silent_audio, vad_filter=False, without_timestamps=True, language=self.language)
        list(segments)



    def transcribe_audio(self, audio):
        segments, _ = self.model.transcribe(audio, vad_filter=True, without_timestamps=True, language=self.language)
        segments_list = list(segments)

        if len(segments_list) != 0:
            full_transcription = " ".join(segment.text for segment in segments_list)
            return full_transcription
        print("Error transcribing. Blank audio?")
        return ""

    def post_process(self, input_string):
        # Check if the last character is not a whitespace
        if input_string and not input_string[-1].isspace():
            input_string += ' '

        # Remove leading whitespace
        return input_string.lstrip()

    # TODO: start and stop methods to release resources

    def set_backend(self, backend):
        pass
    def stop(self):
        self.model = None
        pass
