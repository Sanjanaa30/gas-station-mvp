from pydantic_settings import BaseSettings
from pathlib import Path

class Settings(BaseSettings):
    DATA_DIR: Path = Path(__file__).resolve().parents[2] / "data"

settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
