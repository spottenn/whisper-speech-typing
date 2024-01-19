import signal
import time

from PySide2.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QLabel, QWidgetAction
from PySide2.QtGui import QIcon, QCursor
from PySide2.QtCore import Slot
import sys
from configmanager import ConfigManager
from hotkeyhandler import HotkeyHandler
from localtranscriber import LocalTranscriber
from recorder import Recorder
from settingsinterface import SettingsInterface
from texttyper import TextTyper
from whisperqueue import WhisperQueue
import threading


class SystemTrayApp(QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.hotkey_handler = None
        self.texttyper = None
        self.transcriber = None
        self.recorder = None
        self.message_queue = WhisperQueue()
        self.enabled = False
        self.quitting = False
        print("Initializing application...")

        self.config_manager = ConfigManager()

        # Set up the system tray application
        self.tray_icon = QSystemTrayIcon(QIcon("assets/logo/16/wsp_wait.png"), self)
        self.menu = QMenu()

        self.hotkey_label = QLabel(f"Hold {self.config_manager.get_setting('hotkey')} to type with voice")
        self.hotkey_label_action = QWidgetAction(self)
        self.hotkey_label_action.setDefaultWidget(self.hotkey_label)
        self.menu.addAction(self.hotkey_label_action)

        # Settings action
        self.settings_action = SettingsInterface(self.config_manager, self.menu, self.restart)

        self.menu.addAction(self.settings_action)

        # Add start and stop actions to the system tray menu
        self.start_stop_action = self.menu.addAction("Disable Typing")
        self.start_stop_action.triggered.connect(self.start_stop_typing)

        self.exit_action = self.menu.addAction("Close")
        self.exit_action.triggered.connect(self.close_application)

        self.tray_icon.setContextMenu(self.menu)
        self.tray_icon.activated.connect(self.icon_activated)
        self.tray_icon.show()

        self.display_thread = threading.Thread(target=self.display_state)
        self.display_thread.start()
        self.load_and_initialize_components()
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

        self.start_typing()

    def display_state(self):
        while not self.quitting:
            if self.message_queue.qsize() > 0:
                message = self.message_queue.get()
                status = message["status"]
                if status == "recording":
                    self.tray_icon.setIcon(QIcon("assets/logo/16/wsp_record.png"))
                elif status == "ready":
                    self.tray_icon.setIcon(QIcon("assets/logo/16/wsp_ready.png"))
                elif status == "typing":
                    self.tray_icon.setIcon(QIcon("assets/logo/16/wsp_type.png"))
                elif status == "transcribing" or status == "starting" or status == "stopping" or status == "loading":
                    self.tray_icon.setIcon(QIcon("assets/logo/16/wsp_wait.png"))
                elif status == "disabled":
                    self.tray_icon.setIcon(QIcon("assets/logo/16/wsp_disabled.png"))
                self.tray_icon.setToolTip(status)
            time.sleep(0.1)

    def restart(self):
        self.menu.hide()
        self.stop_typing()
        self.load_and_initialize_components()
        self.start_typing()
        return

    def start_stop_typing(self):
        if self.enabled:
            self.stop_typing()
        else:
            self.start_typing()

    def start_typing(self):
        self.hotkey_handler.start()
        print("Speech typing started.")

        self.enabled = True
        self.start_stop_action.setText("Disable Typing")
        time.sleep(0.1)  # Wait for the system tray icon to update
        self.tray_icon.showMessage("Whisper Speech Typing Started",
                                   f"Hold {self.config_manager.get_setting('hotkey')} to type. \nClick green icon below for more.",
                                   QSystemTrayIcon.Information, 30000)

    def stop_typing(self):
        self.hotkey_handler.stop()
        print("Speech typing stopped.")
        self.enabled = False
        self.start_stop_action.setText("Enable Typing")

    def close_application(self):
        self.stop_typing()
        self.quitting = True
        time.sleep(.6)
        self.quit()

    @Slot(QSystemTrayIcon.ActivationReason)
    def icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # Left click
            # Get the current cursor position
            cursor_position = QCursor.pos()
            # Popup the menu at the cursor's current position
            self.menu.popup(cursor_position)


if __name__ == "__main__":
    app = SystemTrayApp(sys.argv)
    sys.exit(app.exec_())
