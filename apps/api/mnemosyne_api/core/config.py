from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Mnemosyne API"
    database_url: str = "postgresql+psycopg://mnemosyne:mnemosyne@localhost:5432/mnemosyne"
    cors_allowed_origins: str = (
        "http://127.0.0.1:1420,http://tauri.localhost,tauri://localhost"
    )

    @property
    def allowed_origins(self) -> list[str]:
        return [origin.strip() for origin in self.cors_allowed_origins.split(",") if origin.strip()]


settings = Settings()
