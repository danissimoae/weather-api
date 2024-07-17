from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Для получения важных ключей, переменных, паролей"""
    OPENAPI_URL: str = "/openapi.json"
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True
    )
