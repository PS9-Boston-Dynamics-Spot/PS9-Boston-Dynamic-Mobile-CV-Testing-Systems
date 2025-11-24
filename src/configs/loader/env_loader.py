from pathlib import Path
from typing import Dict

from dotenv import dotenv_values

from configs.exceptions.ConfigNotFound import ConfigNotFound
from configs.exceptions.ConfigLoadError import ConfigLoadError


class EnvLoader:
    def load_env(self, file_path: str) -> Dict[str, str]:
        path = Path(file_path)

        if not path.exists():
            raise ConfigNotFound(
                exception=FileNotFoundError(".env file not found"),
                path=file_path,
                error_code=1760795750,
            )

        try:
            # dotenv_values liest die .env-Datei und gibt ein Mapping zurück,
            # Datei wird intern direkt wieder geschlossen.
            values = dotenv_values(path)
            return dict(values)
        except Exception as e:
            raise ConfigLoadError(exception=e, error_code=1760795790)

