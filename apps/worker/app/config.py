from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str
    redis_url: str
    artifacts_path: str = "./artifacts"
    playwright_headless: bool = True
    page_timeout_ms: int = 30_000


settings = Settings()
