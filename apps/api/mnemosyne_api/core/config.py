from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Mnemosyne API"
    database_url: str = "postgresql+psycopg://mnemosyne:mnemosyne@localhost:5432/mnemosyne"


settings = Settings()
