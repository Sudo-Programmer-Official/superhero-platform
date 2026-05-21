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

    @staticmethod
    def _clean_url(value: str) -> str:
        # Deploy env UIs/copy-paste can introduce wrappers or dangling chars.
        url = value.strip().strip("'").strip('"').strip("`")

        # Repeatedly unwrap balanced outer delimiters.
        while len(url) >= 2 and (
            (url[0], url[-1]) in {("(", ")"), ("[", "]"), ("{", "}"), ("<", ">")}
        ):
            url = url[1:-1].strip()

        # Handle common accidental trailing characters in env values.
        url = url.rstrip(");")
        return url

    @property
    def database_url_async(self) -> str:
        url = self._clean_url(self.database_url)
        if url.startswith("postgres://"):
            return "postgresql+asyncpg://" + url[len("postgres://") :]
        if url.startswith("postgresql://"):
            return "postgresql+asyncpg://" + url[len("postgresql://") :]
        return url

    @property
    def database_url_sync_resolved(self) -> str:
        url = self._clean_url(self.database_url_sync or self.database_url)
        if url.startswith("postgres://"):
            return "postgresql://" + url[len("postgres://") :]
        if url.startswith("postgresql+asyncpg://"):
            return "postgresql://" + url[len("postgresql+asyncpg://") :]
        return url

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
