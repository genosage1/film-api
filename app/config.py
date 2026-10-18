from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = "sqlite:///./film.db"
    host: str = "0.0.0.0"
    port: int = 8000

    spider_timeout: int = 15
    spider_delay_min: float = 1.0
    spider_delay_max: float = 3.0


settings = Settings()
