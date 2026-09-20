"""Application configuration loaded from environment variables / .env."""

from urllib.parse import urlsplit

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    env: str = "development"
    debug: bool = True
    log_level: str = "INFO"

    mongodb_url: str = "mongodb://localhost:27017"
    mongodb_db_name: str = "pikupo"

    # Empty => in-memory pub/sub (fine for local dev and single-instance deploys).
    redis_url: str = ""

    jwt_secret: str = "change-me"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24 * 30

    admin_email: str = "admin@example.com"
    admin_password: str = "change-me"

    cors_origins: str = "http://localhost:3000,http://localhost:3006"

    firebase_service_account_json: str = ""

    google_client_id: str = ""
    facebook_app_id: str = ""
    facebook_app_secret: str = ""

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @staticmethod
    def _url_has_real_password(url: str) -> bool:
        """Return True when the connection URL embeds a non-placeholder password."""
        if not url:
            return False
        try:
            netloc = urlsplit(url).netloc
        except ValueError:
            return False
        if "@" not in netloc:
            return False
        userinfo = netloc.rsplit("@", 1)[0]
        password = userinfo.split(":", 1)[1] if ":" in userinfo else ""
        return password.strip() not in ("", "change-me")

    def validate_production_secrets(self) -> None:
        """Refuse to boot in production with placeholder or missing secrets."""
        if self.env.strip().lower() != "production":
            return
        problems: list[str] = []
        if not self.jwt_secret or self.jwt_secret.strip() == "change-me":
            problems.append("JWT_SECRET")
        if not self.admin_password or self.admin_password.strip() == "change-me":
            problems.append("ADMIN_PASSWORD")
        if not self.mongodb_url or not self._url_has_real_password(self.mongodb_url):
            problems.append("MONGODB_URL (must include a non-placeholder password)")
        if not self.redis_url or not self._url_has_real_password(self.redis_url):
            problems.append("REDIS_URL (must include a non-placeholder password)")
        if problems:
            raise RuntimeError(
                "Refusing to start in production: the following secrets are "
                "unset or still placeholder values - "
                + ", ".join(problems)
                + ". Set real values via environment variables."
            )


settings = Settings()
