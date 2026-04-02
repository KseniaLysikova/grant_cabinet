from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    database_url: str = "sqlite:///./grant_cabinet.db"
    secret_key: str = "super-secret-key-change-me"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440
    upload_dir: str = "uploads"
    max_file_size_mb: int = 10
    allowed_file_extensions: str = ".pdf,.doc,.docx,.png,.jpg,.jpeg"
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def allowed_extensions_set(self) -> set[str]:
        return {ext.strip().lower() for ext in self.allowed_file_extensions.split(",") if ext.strip()}


settings = Settings()