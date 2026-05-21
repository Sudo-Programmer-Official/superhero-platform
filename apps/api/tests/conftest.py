import os

os.environ.setdefault("ENV", "test")
os.environ.setdefault("STARTUP_VALIDATION_STRICT", "false")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://postgres:postgres@localhost:5432/superhero_platform")
os.environ.setdefault("DB_SCHEMA", "superhero_platform")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:5173,http://localhost:5174")
os.environ.setdefault("FIREBASE_PROJECT_ID", "test-project")
os.environ.setdefault("AWS_REGION", "us-east-1")
os.environ.setdefault("S3_BUCKET", "test-bucket")
os.environ.setdefault("S3_PREFIX", "superhero-platform/test")
os.environ.setdefault("LOG_LEVEL", "INFO")
os.environ.setdefault("PAYMENTS_TEST_MODE", "true")
