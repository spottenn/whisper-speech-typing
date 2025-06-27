import pyautogui
import pyperclip
import time
import random


class TextTyper:
    def __init__(self):
        pyautogui.PAUSE = 0
        pass

    def type_text(self, text):
        if text is None:
            print("Error, text empty.")
            return

        try:

            # Base typing speed: ~80 WPM (0.15 seconds per character)
            base_delay = 0.10

            for i, char in enumerate(text):
                # Add natural variation to typing speed
                # Faster for common letters, slower for punctuation and capitals
                if char.isupper():
                    delay = base_delay * random.uniform(1.2, 1.8)  # Slower for capitals
                elif char in 'aeioutnshrdl':  # Common letters
                    delay = base_delay * random.uniform(0.7, 1.0)  # Faster for common letters
                else:
                    delay = base_delay * random.uniform(0.9, 1.3)  # Normal variation

                # Occasionally add longer pauses (like thinking pauses)
                if random.random() < 0.04:  # 2% chance
                    delay += random.uniform(0.6, 0.9)
                # Type the character
                pyautogui.write(char)
                # Delay after typing.
                if char == ' ':
                    delay = base_delay * random.uniform(1, 1.9)  # Slight variation for spaces
                elif char in '.,!?;:\n':
                    delay = base_delay * random.uniform(1.5, 2.5)  # Pause at punctuation
                # Don't add delay after the last character
                if i < len(text) - 1:
                    time.sleep(delay)

        except Exception as e:
            print(f"Error while typing: {e}")
    def safe_type_text(self, text):
        pyautogui.typewrite(text)

