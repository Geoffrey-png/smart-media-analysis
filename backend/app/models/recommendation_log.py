from datetime import datetime

from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, Text

from app.db.database import Base


class RecommendationLog(Base):
    __tablename__ = "recommendation_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    content_id = Column(Integer, ForeignKey("contents.id"), nullable=False, index=True)
    scene = Column(String(50), default="mixed", index=True)
    action = Column(String(30), default="exposure", index=True)  # exposure / click
    recommend_score = Column(Float, default=0)
    reason = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

