import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QWidget, QHBoxLayout,
                               QMenu, QWidgetAction)
from PySide6.QtCore import Qt, QPoint, QSize, QThread, Signal, Slot
from PySide6.QtGui import QIcon, QFont
from settingsinterface import SettingsInterface
from configmanager import ConfigManager


class FloatWindow(QMainWindow):
    status_updated = Signal(str, str)
    def __init__(self, config_manager = None, minimize_callback=None, settings_interface=None, close_callback=None, status_button_callback=None, switch_ui_callback=None):
        super().__init__()
        self.config_manager = config_manager or ConfigManager()
        self.minimize_callback = minimize_callback
        self.settings_interface = settings_interface or SettingsInterface(self.config_manager)  # Default to a new instance if none provided
        self.close_callback = close_callback
        self.switch_ui_callback = switch_ui_callback
        self.status_button_callback = status_button_callback
        self.status_updated.connect(self.update_status)

        self.initUI()
        self.oldPos = self.pos()

    def initUI(self):
        # Window setup
        self.setWindowTitle('Speech Application Status')
        self.setGeometry(100, 100, 200, 200)  # Reduced window size
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)


        # Central widget and layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        # TODO: Apply stylesheet to the window or outermost widget applying to self doesn't work because of the frameless window
        # self.rounded_border =("""
        #             _______ {
        #                 border: 2px solid dark gray; /* Thin borderline */
        #                 border-radius: 10px; /* Rounded corners */
        #             }
        #         """)
        # central_widget.setStyleSheet(self.rounded_border) # Is this right?

        # Reduce layout spacing
        layout.setContentsMargins(0, 0, 0, 0)  # This sets all margins to 0
        layout.setSpacing(0)
        top_row_layout = QHBoxLayout()

        # Settings with the same size as the close button
        self.settings_button = QPushButton(central_widget)
        self.settings_button.setIcon(QIcon('./assets/wsp_settings.svg'))  # Replace with gear icon path
        self.settings_button.setFixedSize(30, 30)  # Set the size of the settings button
        self.settings_button.setIconSize(self.settings_button.size()-QSize(5, 5))
        # Settings button with QMenu
        self.settings_menu = QMenu(self)
        self.settings_menu.addAction(self.settings_interface)  # Add SettingsInterface as an action
        self.settings_button.clicked.connect(self.showSettingsMenu)

        # Minimize button, similar to the settings button
        self.minimize_button = QPushButton(central_widget)
        self.minimize_button.setIcon(QIcon('./assets/wsp_minimize.svg'))  # Replace with minimize icon path
        self.minimize_button.setFixedSize(30, 30)  # Set the size of the minimize button
        self.minimize_button.setIconSize(self.minimize_button.size() - QSize(5, 5))
        self.minimize_button.clicked.connect(self.switch_ui_callback)

        # Close button
        self.close_button = QPushButton(central_widget)
        self.close_button.setIcon(QIcon('./assets/wsp_close.svg'))  # Replace with gear icon path
        self.close_button.setFixedSize(30, 30)  # Smaller size for close button
        self.close_button.setIconSize(self.settings_button.size()-QSize(5, 5))
        self.close_button.clicked.connect(self.close_application)

        # Add buttons to the top row
        top_row_layout.addWidget(self.settings_button, 0, Qt.AlignTop | Qt.AlignLeft)
        top_row_layout.addStretch()  # Add stretch to push buttons to the right
        top_row_layout.addWidget(self.minimize_button, 0, Qt.AlignTop | Qt.AlignRight)
        top_row_layout.addWidget(self.close_button, 0, Qt.AlignTop | Qt.AlignRight)

        # Add top row layout to the main layout
        layout.addLayout(top_row_layout)

        # Status image button
        self.status_button = QPushButton(central_widget)
        self.status_button.setFixedSize(64, 64)  # Smaller size for close button
        self.status_button.setIcon(QIcon('./assets/logo/wsp_logo.svg'))
        self.status_button.setIconSize(self.status_button.size())
        if self.status_button_callback:
            self.status_button.clicked.connect(self.status_button_callback)

        layout.addWidget(self.status_button, 0, Qt.AlignCenter)

        # Status text label
        self.status_label = QLabel("Ready", central_widget)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setFont(QFont('Arial', 10, QFont.Bold))
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)

        # Hints label
        self.hints_label = QLabel(f"Hint: Hold {self.config_manager.get_setting('hotkey')} and start speaking to type.", central_widget)
        self.hints_label.setAlignment(Qt.AlignCenter)
        self.hints_label.setFont(QFont('Arial', 10))
        self.hints_label.setWordWrap(True)
        layout.addWidget(self.hints_label)

        # Set layout
        central_widget.setLayout(layout)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def minimizeWindow(self):
        if self.minimize_callback:
            self.minimize_callback()
        self.hide()

    def close_application(self):
        self.close()
        if self.close_callback:
            self.close_callback()
    def set_status_text(self, text):
        self.status_label.setText(text)

    def set_status_icon(self, icon_path):
        icon = QIcon(icon_path)
        self.status_button.setIcon(icon)
        self.status_button.setIconSize(self.status_button.size())

    def set_hint_text(self, text):
        self.hints_label.setText(text)

    def showSettingsMenu(self):
        # Show the settings menu at the current cursor position
        self.settings_menu.exec_(self.cursor().pos())

    @Slot(str, str)
    def update_status(self, icon_name, status_text):
        icon_path = f"assets/png_icons/{icon_name}_128x128.png"
        self.status_button.setIcon(QIcon(icon_path))
        self.status_label.setText(status_text)
        # TODO add hints

def main():
    app = QApplication(sys.argv)
    # Example usage: Define the functions to be used for settings and status button


    def status_function():
        print("Status button pressed")

    window = FloatWindow(minimize_callback=None, status_button_callback=status_function)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
