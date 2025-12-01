from pathlib import Path
from dotenv import dotenv_values
from credentials.env.exceptions.EnvLoadError import EnvLoadError
from credentials.env.exceptions.EnvNotFound import EnvNotFound


class EnvLoader:
    def load_env(self, file_path: str) -> dict[str, str]:
        path = Path(file_path)
        if not path.exists():
            raise EnvNotFound(
                exception=FileNotFoundError("Env file not found"),
                path=file_path,
                error_code=1764010370,
            )

        try:
            values = dotenv_values(path)
            return values
        except Exception as e:
            raise EnvLoadError(exception=e, error_code=1764010380)
