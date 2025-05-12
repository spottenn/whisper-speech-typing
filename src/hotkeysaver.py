import threading
import keyboard
from .whisperqueue import WhisperQueue

class HotkeySaver:
    def __init__(self):
        self._current_keys = set()
        self._all_keys = set()
        self._hotkey_string = ""
        self._done_flag = threading.Event()

    def _handle_hook(self, event):
        print("hooked")
        if event.event_type == keyboard.KEY_DOWN:
            self._current_keys.add(event.name)
            self._all_keys.add(event.name)
        elif event.event_type == keyboard.KEY_UP:
            print("on release", event.name)
            self._current_keys.discard(event.name)
            if not self._current_keys:
                # All keys of the hotkey have been released
                self._hotkey_string = keyboard.get_hotkey_name(self._all_keys)
                self._all_keys = set()
                keyboard.unhook_all()  # Unhook all listeners
                self._done_flag.set()

    def record_hotkey(self):
        keyboard.hook(self._handle_hook)
        self._done_flag.wait()  # Wait until all keys are released
        self._done_flag.clear()  # Reset the flag
        return self._hotkey_string.upper()

