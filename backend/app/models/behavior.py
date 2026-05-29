from datetime import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String

from app.db.database import Base


class UserBehavior(Base):
    __tablename__ = "user_behaviors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False, index=True)
    action_type = Column(String(30), nullable=False, index=True)
    duration = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

