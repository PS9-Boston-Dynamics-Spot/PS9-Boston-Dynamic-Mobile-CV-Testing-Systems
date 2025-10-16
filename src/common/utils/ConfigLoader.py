import yaml
from pathlib import Path
from common.exceptions.ConfigErrors import ConfigNotFound, ConfigParseError

class ConfigLoader:

    def load_config(self, file_path: str) -> dict | None:
        path = Path(file_path)
        if not path.exists():
            message = f"Configuration file not found: {path}"
            ConfigNotFound.log_error(message=message)
            return None
        try:
            with path.open("r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
                if not isinstance(config, dict):
                    message = f"Invalid configuration format in {path}"
                    ConfigParseError.log_error(message=message)
                return config
        except yaml.YAMLError as e:
            message = f"Error parsing YAML file {path}: {e}"
            ConfigParseError.log_exception(message=message)
            return None
        except Exception as e:
            message = f"Error loading configuration file {path}: {e}"
            ConfigParseError.log_exception(message=message)
            return None
