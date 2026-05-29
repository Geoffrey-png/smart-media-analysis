import os
from pathlib import Path


class Settings:
    """应用配置。

    开发阶段默认使用 SQLite，后续可通过 DATABASE_URL 替换为 MySQL/PostgreSQL。
    """

    APP_NAME = "智能传媒内容分析与推荐系统"
    API_PREFIX = "/api"
    BACKEND_DIR = Path(__file__).resolve().parents[2]
    PROJECT_DIR = BACKEND_DIR.parent
    DATA_DIR = BACKEND_DIR / "data"
    UPLOAD_DIR = BACKEND_DIR / "uploads"
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{(DATA_DIR / 'smart_media.db').resolve().as_posix()}",
    )
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "smart-media-demo-secret")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "10080"))
    CORS_ORIGINS = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


settings = Settings()
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
