from queue import Queue


class WhisperQueue(Queue):
    def __init__(self):
        super().__init__()

    def send_message(self, status, component, message):
        self.put({"status": status, "component": component, "message": message})
        print(message)


# Example usage
# whisper_queue = WhisperQueue()
# whisper_queue.send_message("INFO", "This is a test message.")