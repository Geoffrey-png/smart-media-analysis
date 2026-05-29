from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.db.database import Base


class OperationLog(Base):
    __tablename__ = "operation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=True)
    username = Column(String(80), default="")
    role = Column(String(30), default="")
    module = Column(String(60), default="", index=True)
    action = Column(String(80), default="", index=True)
    target_type = Column(String(60), default="")
    target_id = Column(String(80), default="")
    detail = Column(Text, default="")
    ip = Column(String(80), default="")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
