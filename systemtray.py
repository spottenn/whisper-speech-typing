import sys
from PySide2.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QLabel, QWidgetAction, QPushButton
from PySide2.QtGui import QIcon, QCursor
from PySide2.QtCore import Slot, Signal

from configmanager import ConfigManager
from settingsinterface import SettingsInterface
from whisperqueue import WhisperQueue


class SystemTrayApp(QSystemTrayIcon):
    status_updated = Signal(str, str)
    def __init__(self, message_queue: WhisperQueue, config_manager: ConfigManager = None, restart_callback = None, start_stop_callback = None, close_callback = None):
        super().__init__(QIcon())
        self.restart_callback = restart_callback
        self.start_stop_callback = start_stop_callback
        self.config_manager = config_manager or ConfigManager()
        self.message_queue = message_queue
        self.close_callback = close_callback

        self.status_updated.connect(self.update_status)

        # Set up the system tray application
        self.setIcon(QIcon("assets/logo/16/wsp_wait.png"))
        self.menu = QMenu()

        self.hotkey_label = QLabel(f"Hold {self.config_manager.get_setting('hotkey')} to type with voice")
        self.hotkey_label_action = QWidgetAction(self)
        self.hotkey_label_action.setDefaultWidget(self.hotkey_label)
        self.menu.addAction(self.hotkey_label_action)

        self.settings_action = SettingsInterface(self.config_manager, self.menu, self.restart)

        # Advanced Settings Menu
        self.advanced_menu = QMenu("Advanced Settings")

        # Moving settings_action to the advanced menu
        self.advanced_menu.addAction(self.settings_action)

        # Creating a button for Advanced Settings
        self.advanced_menu_button = QPushButton("Advanced Settings")

        # Adding button as a widget action in the main menu
        self.advanced_menu_button_action = QWidgetAction(self)
        self.advanced_menu_button_action.setDefaultWidget(self.advanced_menu_button)
        self.menu.addAction(self.advanced_menu_button_action)
        self.advanced_menu_button.setMenu(self.advanced_menu)

        # Add start and stop actions to the system tray menu
        self.start_stop_action = self.menu.addAction("Disable Typing")
        self.start_stop_action.triggered.connect(self.start_stop_callback)

        self.exit_action = self.menu.addAction("Close")
        self.exit_action.triggered.connect(self.close_application)

        self.setContextMenu(self.menu)
        self.activated.connect(self.icon_activated)
        self.show()
        self.showMessage("Whisper Speech Typing Started",
                         f"Hold {self.config_manager.get_setting('hotkey')} to type. \nClick green icon below for more.",
                         QSystemTrayIcon.Information, 5000)
    def restart(self):
        if self.restart_callback:
            self.restart_callback()
        self.menu.hide()
    @Slot(str, str)
    def update_status(self, icon_name, status_text):
        icon_path = f"assets/logo/16/{icon_name}.png"
        self.setIcon(QIcon(icon_path))
        self.setToolTip(status_text)
        if status_text == "disabled":
            self.start_stop_action.setText("Enable Typing")
        if status_text == "ready":
            self.start_stop_action.setText("Disable Typing")


    @Slot(QSystemTrayIcon.ActivationReason)
    def icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # Left click
            # Get the current cursor position
            cursor_position = QCursor.pos()
            # Popup the menu at the cursor's current position
            self.menu.popup(cursor_position)
    def close_application(self):
        self.hide()
        if self.close_callback:
            self.close_callback()


if __name__ == "__main__":
    app = SystemTrayApp(WhisperQueue())
    sys.exit(app.exec_())