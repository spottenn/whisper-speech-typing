from abc import ABC, abstractmethod
from PySide2.QtCore import QObject

# Abstract class defining the common interface
class GuiComponent(ABC):

    def __init__(self):
        super().__init__()

    @abstractmethod
    def update_status(self, icon_path, status_text):
        pass