"""初始化数据库和测试数据。

两种模式：
  重置模式（默认）：python scripts/init_db.py          → 删库 + 建表 + 播种
  安全模式          ：python scripts/init_db.py --safe   → 仅当库为空时播种

运行：
    cd backend
    .\.venv\Scripts\python scripts\init_db.py
"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.db.database import Base, SessionLocal, engine  # noqa: E402
from app.db.seed import seed_demo_data  # noqa: E402


def reset_and_seed():
    """完整重置：清空数据库、重建表、写入演示数据。"""
    print("正在重置数据库...")
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_demo_data(db)
        db.commit()
    finally:
        db.close()
    print("数据库重置完成（已清空并重新播种）。")


def safe_seed():
    """安全播种：仅当数据库不存在任何用户时才写入演示数据。"""
    from app.models.user import User

    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        from app.db.seed import seed_if_empty

        if seed_if_empty(db):
            print("数据库为空，已自动播种演示数据。")
        else:
            print("数据库已有数据，跳过初始化（使用 --force 可强制重置）。")
    finally:
        db.close()


if __name__ == "__main__":
    if "--safe" in sys.argv:
        safe_seed()
    else:
        reset_and_seed()
