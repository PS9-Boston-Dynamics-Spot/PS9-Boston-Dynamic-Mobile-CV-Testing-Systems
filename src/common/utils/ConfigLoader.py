import yaml
from pathlib import Path
from common.exceptions.ConfigErrors import (
    ConfigNotFound,
    ConfigParseError,
    ConfigLoadError,
)


class ConfigLoader:

    def load_config(self, file_path: str) -> dict:
        path = Path(file_path)
        if not path.exists():
            raise ConfigNotFound(
                exception=FileNotFoundError, path=file_path, error_code=1760794750
            )
        try:
            with path.open("r", encoding="utf-8") as file:
                config = yaml.safe_load(file)
                if not isinstance(config, dict):
                    raise ConfigParseError(
                        exception=NotADirectoryError, error_code=1760794770
                    )
                return config
        except yaml.YAMLError as e:
            raise ConfigLoadError(exception=e, error_code=1760794780)
        except Exception as e:
            raise ConfigLoadError(exception=e, error_code=1760794790)
