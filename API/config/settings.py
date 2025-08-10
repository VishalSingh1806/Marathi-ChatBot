import os
from functools import lru_cache

@lru_cache()
def get_settings():
    return {
        "allowed_origins": os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:5173,http://127.0.0.1:3000,http://127.0.0.1:5173").split(","),
        "redis_host": os.getenv("REDIS_HOST", "localhost"),
        "redis_port": int(os.getenv("REDIS_PORT", 6379)),
        "redis_db": int(os.getenv("REDIS_DB", 0)),
        "redis_password": os.getenv("REDIS_PASSWORD"),
        "sentry_dsn": os.getenv("SENTRY_DSN"),
        "environment": os.getenv("ENVIRONMENT", "production"),
        "gemini_api_key": os.getenv("GEMINI_API_KEY")
    }