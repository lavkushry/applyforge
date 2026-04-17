from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_existing_path(raw_path: str, *, anchor: Path | None = None, cwd: Path | None = None) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path

    anchor_path = (anchor or Path(__file__)).resolve()
    search_roots: list[Path] = []

    if cwd is not None:
        search_roots.append(cwd.resolve())
    else:
        search_roots.append(Path.cwd().resolve())

    search_roots.extend([anchor_path.parent, *anchor_path.parents, Path("/")])

    seen: set[Path] = set()
    for root in search_roots:
        if root in seen:
            continue
        seen.add(root)
        candidate = (root / path).resolve()
        if candidate.exists():
            return candidate

    raise FileNotFoundError(f"Could not resolve path '{raw_path}' from anchor '{anchor_path}'")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    app_name: str = "ApplyForge API"
    env: str = "dev"
    web_origin: str = "http://localhost:3000"
    database_url: str = "sqlite:///./applyforge.db"
    redis_url: str = "redis://localhost:6379/0"
    secret_key: str
    access_token_expire_minutes: int = 120
    access_cookie_name: str = "applyforge_session"
    access_cookie_secure: bool = False
    openai_base_url: str = "https://api.openai.com/v1"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    google_oauth_client_id: str = ""
    google_oauth_client_secret: str = ""
    google_oauth_redirect_uri: str = "http://localhost:8000/inbox/gmail/oauth/callback"
    microsoft_oauth_client_id: str = ""
    microsoft_oauth_client_secret: str = ""
    microsoft_oauth_tenant: str = "common"
    microsoft_oauth_redirect_uri: str = "http://localhost:8000/inbox/outlook/oauth/callback"
    storage_path: str = "./uploads"
    artifacts_path: str = "./artifacts"
    bootstrap_default_user: bool = False
    bootstrap_default_user_email: str = "defaultuser@applyforge.dev"
    bootstrap_default_user_password: str = "defaultuser123"
    prompt_root: str = Field(default="packages/prompts")
    enable_prompt_stub_fallback: bool = True

    @property
    def cors_origins(self) -> list[str]:
        return [self.web_origin]

    @property
    def resolved_prompt_root(self) -> Path:
        return _resolve_existing_path(self.prompt_root)

    @property
    def resolved_config_root(self) -> Path:
        return _resolve_existing_path("packages/config")


settings = Settings()
