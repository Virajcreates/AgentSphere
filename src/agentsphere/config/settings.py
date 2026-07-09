from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/agentsphere"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/agentsphere"
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20


class RedisSettings(BaseSettings):
    REDIS_URL: str = "redis://localhost:6379/0"


class AuthSettings(BaseSettings):
    JWT_SECRET: str = "dev-secret-key-change-in-production-min-32-chars"
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    API_KEY_PREFIX: str = "as_live"
    SEED_ADMIN_EMAIL: str = "admin@agentsphere.local"
    SEED_ADMIN_PASSWORD: str = ""


class TelemetrySettings(BaseSettings):
    OTEL_SERVICE_NAME: str = "agentsphere-api"
    OTEL_EXPORTER_OTLP_ENDPOINT: str = ""
    PROMETHEUS_ENABLED: bool = False
    LANGSMITH_API_KEY: str = ""
    LANGSMITH_PROJECT: str = ""


class RateLimitSettings(BaseSettings):
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60


class Settings(
    DatabaseSettings,
    RedisSettings,
    AuthSettings,
    TelemetrySettings,
    RateLimitSettings,
):
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    APP_VERSION: str = "0.1.0"
    APP_BUILD_TIMESTAMP: str = ""
    GIT_COMMIT: str = ""

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    def validate_required(self) -> list[str]:
        errors: list[str] = []
        if self.ENVIRONMENT == "production":
            if self.JWT_SECRET == "dev-secret-key-change-in-production-min-32-chars":
                errors.append("JWT_SECRET must be changed in production")
            if not self.DATABASE_URL.startswith("postgresql+asyncpg://"):
                errors.append("DATABASE_URL must be a valid async PostgreSQL URL")
            if not self.REDIS_URL.startswith("redis://"):
                errors.append("REDIS_URL must be a valid Redis URL")
        return errors
