from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_name: str = "ApplyForge API"
    env: str = "dev"
    web_origin: str = "http://localhost:3000"
    database_url: str = "sqlite:///./applyforge.db"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str = "applyforge-dev-secret"
    access_token_expire_minutes: int = 120
    access_cookie_name: str = "applyforge_session"
    access_cookie_secure: bool = False
    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    storage_path: str = "./uploads"
    artifacts_path: str = "./artifacts"
    prompt_root: str = Field(default="../../packages/prompts")
    enable_prompt_stub_fallback: bool = True

    @property
    def cors_origins(self) -> list[str]:
        return [self.web_origin]

    @property
    def resolved_prompt_root(self) -> Path:
        return (Path(__file__).resolve().parents[3] / self.prompt_root).resolve()


settings = Settings()
