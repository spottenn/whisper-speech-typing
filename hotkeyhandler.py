import keyboard
import time
from whisperqueue import WhisperQueue


class HotkeyHandler:

    def __init__(self, hotkey, retype_hotkey, recorder, transcriber, texttyper, message_queue: WhisperQueue = WhisperQueue()):
        self.hotkey = hotkey
        self.retype_hotkey = retype_hotkey
        self.recorder = recorder
        self.transcriber = transcriber
        self.text_typer = texttyper
        self.transcription = ""
        self.message_queue = message_queue
        self.running = False
        self.thread = None

    def start_recording(self):
        if not self.recorder.is_recording:
            self.message_queue.send_message("recording", "HotkeyHandler", "Capturing audio...")
            self.recorder.start_audio_capture()

    def stop_recording(self):
        audio = self.recorder.stop_audio_capture()
        self.message_queue.send_message("transcribing", "HotkeyHandler", "Transcribing audio...")
        self.transcription = self.transcriber.transcribe_audio(audio)
        self.transcription = self.transcriber.post_process(self.transcription)
        self.type_transcription()

    def type_transcription(self):
        self.message_queue.send_message("typing", "HotkeyHandler", "Typing out transcription...")
        self.text_typer.type_text(self.transcription)
        self.message_queue.send_message("ready", "HotkeyHandler", "Done typing transcription")

    def start(self):
        if not self.running:
            self.running = True
            # Register hotkeys
            keyboard.add_hotkey(self.hotkey, self.start_recording, suppress=True)
            keyboard.add_hotkey(self.hotkey, self.stop_recording, trigger_on_release=True, suppress=True)
            keyboard.add_hotkey(self.retype_hotkey, self.type_transcription, suppress=True)
            self.message_queue.send_message("ready", "HotkeyHandler", "Ready for hotkeys.")

    def stop(self):
        if self.running:
            self.running = False
            keyboard.unhook_all_hotkeys()
            self.recorder.stop_audio_capture()
            self.recorder.stream.close()
            self.recorder.p.terminate()
            self.message_queue.send_message("disabled", "HotkeyHandler", "HotkeyHandler stopped.")

    def __del__(self):
        self.stop()

    def main(self):
        print(f"Press and hold {self.hotkey} and start speaking. Release to type.")
        print(f"Press {self.retype_hotkey} to retype the most recent speech. Press Ctrl + C to exit")

        self.start()  # Start the HotkeyHandler in its own thread

        try:
            while True:  # Main loop to keep the script running
                time.sleep(1)  # Sleep to reduce CPU usage, can be adjusted
        except KeyboardInterrupt:
            print("Keyboard interrupt detected. Stopping transcriber...")
            self.stop()
            time.sleep(1)  # Give the stream and model time to shut down
