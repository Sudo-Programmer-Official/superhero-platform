from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit


class Settings(BaseSettings):
    env: str = "development"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/superhero_platform"
    database_url_sync: str = "postgresql://postgres:postgres@localhost:5432/superhero_platform"
    db_schema: str = "superhero_platform"
    cors_origins: str = "http://localhost:5173,http://localhost:5174"

    # Firebase Auth settings (verification + issuer validation)
    firebase_project_id: str = ""
    firebase_check_revoked: bool = False
    firebase_service_account_path: str = ""
    firebase_service_account_json: str = ""
    aws_region: str = "us-east-1"
    s3_bucket: str = "openmat-media-prod"
    s3_prefix: str = "superhero-platform"
    s3_presign_expires_seconds: int = 900
    stripe_secret_key: str = ""
    stripe_webhook_secret: str = ""
    stripe_connect_client_id: str = ""
    stripe_country: str = "US"
    payments_enabled: bool = False
    payments_test_mode: bool = False
    startup_validation_strict: bool = True
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
            url = "postgresql+asyncpg://" + url[len("postgres://") :]
        if url.startswith("postgresql://"):
            url = "postgresql+asyncpg://" + url[len("postgresql://") :]
        return self._normalize_asyncpg_url(url)

    @staticmethod
    def _normalize_asyncpg_url(url: str) -> str:
        # asyncpg does not support `sslmode`; map it to `ssl` for runtime URLs.
        if not url.startswith("postgresql+asyncpg://"):
            return url
        parsed = urlsplit(url)
        query_pairs = parse_qsl(parsed.query, keep_blank_values=True)
        normalized: list[tuple[str, str]] = []
        for key, value in query_pairs:
            if key == "sslmode":
                if value.strip():
                    normalized.append(("ssl", value))
                continue
            normalized.append((key, value))
        return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(normalized), parsed.fragment))

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

    @property
    def required_env_keys(self) -> list[str]:
        keys = [
            "DATABASE_URL",
            "DB_SCHEMA",
            "CORS_ORIGINS",
            "FIREBASE_PROJECT_ID",
            "AWS_REGION",
            "S3_BUCKET",
            "S3_PREFIX",
            "LOG_LEVEL",
        ]
        if self.payments_enabled and not self.payments_test_mode:
            keys.extend(
                [
                    "STRIPE_SECRET_KEY",
                    "STRIPE_WEBHOOK_SECRET",
                ]
            )
        return keys


settings = Settings()
