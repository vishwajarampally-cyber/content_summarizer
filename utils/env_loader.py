from pathlib import Path

from dotenv import load_dotenv


def load_project_env() -> None:
    root = Path(__file__).resolve().parents[1]
    env_paths = [
        root / ".env",
        root / ".venv" / ".env",
    ]

    for env_path in env_paths:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path, override=False)
            return

    load_dotenv(override=False)
