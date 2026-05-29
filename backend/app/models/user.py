from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(80), nullable=False, unique=True, index=True)
    nickname = Column(String(80), default="")
    password_hash = Column(String(255), default="")
    role = Column(String(30), default="viewer", index=True)
    status = Column(String(30), default="active", index=True)
    age = Column(Integer, default=0)
    gender = Column(String(20), default="unknown")
    city = Column(String(80), default="")
    interests = Column(Text, default="")
    profile_vector = Column(Text, default="")  # JSON：由行为实时计算的画像权重
    active_score = Column(Float, default=0)
    last_active_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
