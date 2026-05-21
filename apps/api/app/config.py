from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    env: str = "development"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/superhero_platform"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/superhero_platform"
    db_schema: str = "superhero_platform"
    cors_origins: str = "http://localhost:5173,http://localhost:5174"

    # Firebase Auth settings (verification + issuer validation)
    firebase_project_id: str = ""
    aws_region: str = "us-east-1"
    s3_bucket: str = "openmat-media-prod"
    s3_prefix: str = "superhero-platform"
    s3_presign_expires_seconds: int = 900
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_connect_client_id: str = ""
    stripe_country: str = "US"
    payments_test_mode: bool = False
    log_level: str = "INFO"
    log_format: str = "json"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
