from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    app_name: str = 'ApplyForge API'
    env: str = 'dev'
    database_url: str
    redis_url: str
    secret_key: str
    access_token_expire_minutes: int = 120
    openai_base_url: str = 'https://api.openai.com/v1'
    openai_api_key: str = ''
    openai_model: str = 'gpt-4o-mini'
    storage_path: str = './uploads'


settings = Settings()
