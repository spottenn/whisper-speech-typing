import time

from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidgetAction, QWidget, QVBoxLayout, QLabel, QComboBox, QHBoxLayout, QLineEdit, \
    QPushButton

from hotkeysaver import HotkeySaver

class SettingsInterface(QWidgetAction):
    def __init__(self, config_manager, parent=None, save_settings_callback=None):
        super(SettingsInterface, self).__init__(parent)
        self.config_manager = config_manager
        self.hotkey_recorder = HotkeySaver()
        self.save_callback = save_settings_callback

        widget = QWidget()
        self.widget = widget
        layout = QVBoxLayout(widget)

        # Hotkey settings
        layout.addWidget(QLabel("Type With Voice"))
        hotkey_layout = QHBoxLayout()
        self.hotkey_input = QLineEdit(config_manager.get_setting('hotkey'))
        hotkey_layout.addWidget(self.hotkey_input)
        self.record_hotkey_button = QPushButton("Record")
        self.record_hotkey_button.clicked.connect(self.record_start_stop_hotkey)
        hotkey_layout.addWidget(self.record_hotkey_button)
        self.reset_hotkey_button = QPushButton("Reset")
        self.reset_hotkey_button.clicked.connect(lambda: self.hotkey_input.setText("f4"))
        hotkey_layout.addWidget(self.reset_hotkey_button)
        layout.addLayout(hotkey_layout)

        # Retype hotkey settings
        layout.addWidget(QLabel("Type the Most Recent Speech Again (tap)"))
        retype_hotkey_layout = QHBoxLayout()
        self.retype_hotkey_input = QLineEdit(config_manager.get_setting('type_hotkey'))
        retype_hotkey_layout.addWidget(self.retype_hotkey_input)
        self.record_retype_hotkey_button = QPushButton("Record")
        self.record_retype_hotkey_button.clicked.connect(self.record_retype_hotkey)
        retype_hotkey_layout.addWidget(self.record_retype_hotkey_button)
        self.reset_retype_hotkey_button = QPushButton("Reset")
        self.reset_retype_hotkey_button.clicked.connect(lambda: self.retype_hotkey_input.setText("f2"))
        retype_hotkey_layout.addWidget(self.reset_retype_hotkey_button)
        layout.addLayout(retype_hotkey_layout)

        # Device settings
        device_layout = QHBoxLayout()
        device_layout.addWidget(QLabel("Device:"))
        self.device_input = QComboBox()
        self.device_input.addItems(["gpu", "cpu"])
        self.device_input.setCurrentText(self.config_manager.get_setting('device'))
        device_layout.addWidget(self.device_input)
        layout.addLayout(device_layout)

        # Model size settings
        model_size_layout = QHBoxLayout()
        model_size_layout.addWidget(QLabel("Model Size:"))
        self.model_size_input = QComboBox()
        self.model_size_input.addItems([
            "tiny", "tiny.en",
            "base", "base.en",
            "small", "small.en",
            "medium", "medium.en",
            "large",
            "large-v2",
            "large-v3"
        ])
        self.model_size_input.setCurrentText(self.config_manager.get_setting('model_size'))
        model_size_layout.addWidget(self.model_size_input)
        layout.addLayout(model_size_layout)

        # Save button
        save_button = QPushButton("Save")
        save_button.clicked.connect(self.save_settings)
        layout.addWidget(save_button)


        self.setDefaultWidget(widget)

    def record_hotkey(self, target_input, button):
        button.setText("Recording...")
        time.sleep(1)
        hotkey = self.hotkey_recorder.record_hotkey()
        target_input.setText(hotkey)
        button.setText("Record")

    @Slot()
    def record_start_stop_hotkey(self):
        print("Recording Start/Stop Hotkey...")
        self.record_hotkey(self.hotkey_input, self.record_hotkey_button)

    @Slot()
    def record_retype_hotkey(self):
        print("Recording Retype Hotkey...")
        self.record_hotkey(self.retype_hotkey_input, self.record_retype_hotkey_button)

    @Slot()
    def save_settings(self):
        print("Saving settings...")
        # Update settings using config manager
        self.config_manager.update_setting('device', self.device_input.currentText())
        self.config_manager.update_setting('model_size', self.model_size_input.currentText())
        self.config_manager.update_setting('hotkey', self.hotkey_input.text())
        self.config_manager.update_setting('type_hotkey', self.retype_hotkey_input.text())
        if self.save_callback is not None:
            self.save_callback()
        print("Settings saved.")
