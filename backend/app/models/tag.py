from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from app.db.database import Base


class Tag(Base):
    __tablename__ = "tags"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(80), nullable=False, unique=True, index=True)
    count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

