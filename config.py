from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "Finance Tracking System"
    secret_key: str = "super-secret-key-change-in-production-please"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours
    database_url: str = "sqlite:///./finance.db"

    class Config:
        env_file = ".env"


settings = Settings()
