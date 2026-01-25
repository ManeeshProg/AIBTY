from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings
import os
class Settings(BaseSettings):
    PROJECT_NAME: str = "Am I Better Than Yesterday?"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "changeme_in_production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 days
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL")

    # OpenAI
    OPENAI_API_KEY: str | None = None

    # Anthropic (for scoring enhancement)
    ANTHROPIC_API_KEY: str | None = None

    # Redis / Celery
    REDIS_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str | None = None  # Optional, can use Redis

    @property
    def celery_broker_url(self) -> str:
        return self.REDIS_URL

    @property
    def celery_result_backend_url(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL

    # CORS
    BACKEND_CORS_ORIGINS: List[AnyHttpUrl] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "ignore"  # Ignore extra fields from .env

settings = Settings()
