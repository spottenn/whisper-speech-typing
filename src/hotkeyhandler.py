import threading
import keyboard
import time
from .whisperqueue import WhisperQueue


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
        self.keyboard_lock = threading.Lock()
        self.start()

    def start_recording(self):
        if not self.recorder.is_recording:
            print("getting  lock")
            self.keyboard_lock.acquire()
            self.message_queue.send_message("recording", "HotkeyHandler", "Capturing audio...")
            self.recorder.start_audio_capture()

    def stop_recording(self):
        print("releasing lock")
        if self.keyboard_lock.locked():
            self.keyboard_lock.release()
        audio = self.recorder.stop_audio_capture()
        self.message_queue.send_message("transcribing", "HotkeyHandler", "Transcribing audio...")
        self.transcription = self.transcriber.transcribe_audio(audio)
        self.type_transcription()

    def type_transcription(self):
        self.message_queue.send_message("typing", "HotkeyHandler", "Typing out transcription...")
        self.text_typer.type_text(self.transcription)
        self.message_queue.send_message("ready", "HotkeyHandler", "Done typing transcription")

    def retype_transcription(self):
        self.message_queue.send_message("typing", "HotkeyHandler", "Retyping transcription (safe)")
        self.text_typer.safe_type_text(self.transcription)
        self.message_queue.send_message("ready", "HotkeyHandler", "Done retyping transcription")

    def start(self):
        if not self.running:
            self.running = True
            self.register_hotkeys()
            self.start_heartbeat()
            self.message_queue.send_message("ready", "HotkeyHandler", "Ready for hotkeys.")

    def stop(self):
        if self.running:
            self.running = False
            with self.keyboard_lock:
                keyboard.unhook_all_hotkeys()
            self.recorder.stop_audio_capture()
            self.recorder.stream.close()
            self.recorder.p.terminate()
            self.message_queue.send_message("disabled", "HotkeyHandler", "HotkeyHandler stopped.")
    def register_hotkeys(self):
        with self.keyboard_lock:
            # Register hotkeys
            keyboard.add_hotkey(self.hotkey, self.start_recording, suppress=True)
            keyboard.add_hotkey(self.hotkey, self.stop_recording, trigger_on_release=True, suppress=True)
            keyboard.add_hotkey(self.retype_hotkey, self.retype_transcription, suppress=True)
    def start_heartbeat(self):
        # TODO: permanent fix hotkeys getting unregistered
        def fix_hotkeys():
            while self.running:

                time.sleep(5)
                # start_time = time.time()
                with self.keyboard_lock:
                    keyboard.unhook_all_hotkeys()
                self.register_hotkeys()
                # print(f"Time taken to register hotkeys: {time.time() - start_time:.6f} seconds")

        threading.Thread(target=fix_hotkeys).start()


    def __del__(self):
        self.stop()
        del self.transcriber

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
