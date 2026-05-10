import os

from dotenv import load_dotenv

load_dotenv()


def get_database_url() -> str:
    url = os.getenv("DATABASE_URL", "sqlite:///./building_api.db")
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


def get_cors_origins() -> list[str]:
    origins = os.getenv(
        "CORS_ORIGIN",
        "http://localhost:3000,http://127.0.0.1:3000",
    )
    return [origin.strip() for origin in origins.split(",") if origin.strip()]


def get_app_host() -> str:
    return os.getenv("APP_HOST", "0.0.0.0")


def get_port() -> int:
    return int(os.getenv("PORT", "8000"))
