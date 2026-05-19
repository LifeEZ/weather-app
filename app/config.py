from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    openweathermap_api_key: str
    database_url: str
    rate_limit: str = "30/minute"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8"
    )


settings = Settings()
