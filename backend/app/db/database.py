from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.core.config import settings


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI 数据库会话依赖。"""

    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_sqlite_schema():
    """为开发期 SQLite 做轻量字段兼容。

    SQLAlchemy 的 create_all 不会给已有表自动加新字段，所以这里补齐新增字段。
    正式项目建议改用 Alembic 迁移。
    """

    if not settings.DATABASE_URL.startswith("sqlite"):
        return

    content_columns = {
        "status": "VARCHAR(30) DEFAULT 'published'",
        "audit_comment": "TEXT DEFAULT ''",
        "auditor": "VARCHAR(100) DEFAULT ''",
        "audit_time": "DATETIME",
        "sensitive_words": "TEXT DEFAULT ''",
        "source_name": "VARCHAR(120) DEFAULT ''",
        "source_url": "VARCHAR(800) DEFAULT ''",
    }
    user_columns = {
        "role": "VARCHAR(30) DEFAULT 'viewer'",
        "status": "VARCHAR(30) DEFAULT 'active'",
        "profile_vector": "TEXT DEFAULT ''",
        "active_score": "FLOAT DEFAULT 0",
        "last_active_at": "DATETIME",
    }

    with engine.begin() as conn:
        rows = conn.execute(text("PRAGMA table_info(contents)")).fetchall()
        existing = {row[1] for row in rows}
        for name, definition in content_columns.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE contents ADD COLUMN {name} {definition}"))

        rows = conn.execute(text("PRAGMA table_info(users)")).fetchall()
        existing = {row[1] for row in rows}
        for name, definition in user_columns.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE users ADD COLUMN {name} {definition}"))

        # 演示用户默认角色：tech_user 是管理员，其余按运营场景分配。
        conn.execute(text("UPDATE users SET role='admin' WHERE username='tech_user'"))
        conn.execute(text("UPDATE users SET role='editor' WHERE username='finance_user' AND (role IS NULL OR role='' OR role='viewer')"))
        conn.execute(text("UPDATE users SET role='auditor' WHERE username='ent_user' AND (role IS NULL OR role='' OR role='viewer')"))
        conn.execute(text("UPDATE users SET role='viewer' WHERE role IS NULL OR role=''"))
        conn.execute(text("UPDATE users SET status='active' WHERE status IS NULL OR status=''"))
