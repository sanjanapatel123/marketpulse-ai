from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "MarketPulse AI"
    mongodb_url: str
    mongodb_database: str = "marketpulse"
    frontend_url: str = "http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )
    alert_evaluation_interval_seconds: int = 15
    enable_alert_monitor: bool = True

@lru_cache
def get_settings() -> Settings:
    return Settings()