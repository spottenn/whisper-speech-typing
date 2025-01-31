import pyautogui
import pyperclip
import time


class TextTyper:
    def __init__(self):
        pass

    def type_text(self, text):
        if text is None:
            print("Error, text empty.")
            return
        try:
            # Save the current clipboard content
            original_clipboard_content = pyperclip.paste()

            # Copy the new text to the clipboard
            pyperclip.copy(text)
            time.sleep(0.1)  # Give a brief moment for the clipboard to update

            # Simulate the Ctrl+V keystroke to paste
            pyautogui.hotkey('ctrl', 'v')
            # TODO: Revert this temporary workaround for input leap.
            # # Wait a bit to ensure text is pasted before restoring clipboard
            # time.sleep(0.1)
            #
            # # Restore the original clipboard content
            # pyperclip.copy(original_clipboard_content)
        except Exception as e:
            print(e)
    def safe_type_text(self, text):
        pyautogui.typewrite(text)
