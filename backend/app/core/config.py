from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve .env relative to this file: backend/app/core/config.py -> backend/.env
_ENV_FILE = Path(__file__).resolve().parents[2] / ".env"

class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "RapiStock"
    
    # Secrets
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: int
    # Security
    SECRET_KEY: str
    ALGORITHM: str = "HS256"               # Default config if not exists!
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30  # Default config if not exists!

    # To find .env out here
    model_config = SettingsConfigDict(
        env_file="../.env", 
        env_ignore_empty=True,
        extra="ignore"
    )

    @property
    def SQLALCHEMY_DATABASE_URI(self) -> str:
        # URL for SQLAlchemy
        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

settings = Settings()