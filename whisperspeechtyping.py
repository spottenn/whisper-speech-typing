import signal
import time
import sys

from PySide6.QtWidgets import QApplication
from src.configmanager import ConfigManager
from src.hotkeyhandler import HotkeyHandler
from src.localtranscriber import LocalTranscriber
from src.recorder import Recorder
from src.texttyper import TextTyper
from src.whisperqueue import WhisperQueue
import threading
import gc
from src.systemtray import SystemTrayApp
from src.floatwindow import FloatWindow


class WhisperTypingApp(QApplication):
    def __init__(self):
        super().__init__()
        self.message_queue = WhisperQueue()
        self.enabled = False
        self.quitting = False
        print("Initializing application...")
        self.config_manager = ConfigManager()
        self.floating_window = FloatWindow(config_manager=self.config_manager, minimize_callback=self.switch_gui,
                                           close_callback=self.close_application, switch_ui_callback=self.switch_gui)
        self.system_tray = SystemTrayApp(message_queue=self.message_queue, config_manager=self.config_manager,
                                         restart_callback=self.restart, start_stop_callback=self.start_stop_typing,
                                         close_callback=self.close_application, switch_ui_callback=self.switch_gui)
        if self.config_manager.get_setting('active_gui') == 'floating':
            self.active_gui = self.floating_window
        else:
            self.active_gui = self.system_tray

        self.active_gui.show()
        self.display_thread = threading.Thread(target=self.display_state)
        self.display_thread.start()
        self.start_typing()
        self.message_queue.send_message("ready", "SystemTray", "Application initialized.")


    def load_and_initialize_components(self):
        # Load and initialize components
        # Access model size, device, language, and buffer settings from config
        model_size = self.config_manager.get_setting('model_size')
        device = self.config_manager.get_setting('device')
        if device == 'gpu':
            device = 'cuda'
        # will need to be re-implemented if other backends are added

        language = self.config_manager.get_setting('language')
        buffer = self.config_manager.get_setting('buffer')
        compute_type = self.config_manager.get_setting('compute_type')

        self.recorder = Recorder(buffer=buffer, message_queue=self.message_queue)  # Pass buffer setting
        self.transcriber = LocalTranscriber(
            model_size=model_size, compute_type=compute_type, language=language, device=device,
            message_queue=self.message_queue
        )  # Pass model settings
        self.texttyper = TextTyper()

        # Initialize HotkeyHandler with start and stop capabilities
        self.hotkey_handler = HotkeyHandler(hotkey=self.config_manager.get_setting('hotkey'),
                                            retype_hotkey=self.config_manager.get_setting('type_hotkey'),
                                            recorder=self.recorder,
                                            transcriber=self.transcriber,
                                            texttyper=self.texttyper,
                                            message_queue=self.message_queue)


    def display_state(self):
        while not self.quitting:
            if self.message_queue.qsize() > 0:
                message = self.message_queue.get()
                status = message["status"]

                # Mapping of status to icon names
                status_to_icon = {
                    "recording": "wsp_record",
                    "ready": "wsp_ready",
                    "typing": "wsp_type",
                    "transcribing": "wsp_wait",
                    "starting": "wsp_wait",
                    "stopping": "wsp_wait",
                    "loading": "wsp_wait",
                    "disabled": "wsp_disabled"
                }

                # Default icon name if the status is not found in the dictionary
                icon_name = status_to_icon.get(status, "wsp_disabled")

                self.floating_window.status_updated.emit(icon_name, status)
                self.system_tray.status_updated.emit(icon_name, status)

            time.sleep(0.1)

    def switch_gui(self):
        self.active_gui.hide()
        if self.active_gui == self.floating_window:
            self.active_gui = self.system_tray
            self.config_manager.update_setting('active_gui', 'systemtray')
        else:
            self.active_gui = self.floating_window
            self.config_manager.update_setting('active_gui', 'floating')
        self.active_gui.show()
    def restart(self):
        self.stop_typing()
        self.start_typing()
        return

    def start_stop_typing(self):
        if self.enabled:
            self.stop_typing()
        else:
            self.start_typing()

    def start_typing(self):
        # TODO: start transcriber
        self.load_and_initialize_components()
        print("Speech typing started.")
        self.enabled = True

    def stop_typing(self):
        # TODO:stop transcriber
        self.hotkey_handler.stop()

        self.transcriber.stop()
        gc.collect()
        print("Speech typing stopped.")
        self.enabled = False

    def close_application(self):
        self.stop_typing()
        self.quitting = True
        time.sleep(.6)
        self.quit()


if __name__ == "__main__":
    app = WhisperTypingApp()
    sys.exit(app.exec_())
