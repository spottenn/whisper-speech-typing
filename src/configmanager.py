import json

class ConfigManager:
    def __init__(self, config_file='settings.json'):
        self.config_file = config_file
        self.settings = self.load_config()


    def load_config(self):
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {
                "model_size": "large-v2",
                "device": "cuda",
                "compute_type": "float16",
                "language": "en",
                "hotkey": "f4",
                "type_hotkey": "f2",
                "buffer": True,
            }

    def save_settings(self, settings):
        with open(self.config_file, 'w') as f:
            json.dump(settings, f)
        self.settings = settings

    def get_setting(self, key):
        return self.settings.get(key)

    def update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings(self.settings)
