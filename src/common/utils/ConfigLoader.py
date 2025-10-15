import yaml


class ConfigLoader:
    def __init__(self):
        pass

    def load_config(self, file_path):
        with open(file_path, "r") as file:
            config = yaml.safe_load(file)
        return config
