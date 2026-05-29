from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from app.db.database import Base


class Content(Base):
    __tablename__ = "contents"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, index=True)
    summary = Column(Text, default="")
    content = Column(Text, nullable=False)
    author = Column(String(100), default="系统编辑")
    category = Column(String(50), default="未分类", index=True)
    tags = Column(Text, default="")
    cover_url = Column(String(500), default="")
    source_name = Column(String(120), default="", index=True)
    source_url = Column(String(800), default="", index=True)
    content_type = Column(String(50), default="article", index=True)
    publish_time = Column(DateTime, default=datetime.utcnow, index=True)
    view_count = Column(Integer, default=0)
    like_count = Column(Integer, default=0)
    favorite_count = Column(Integer, default=0)
    comment_count = Column(Integer, default=0)
    heat_score = Column(Float, default=0)
    quality_score = Column(Float, default=0)
    sentiment = Column(String(20), default="neutral")
    status = Column(String(30), default="published", index=True)  # draft/pending/published/rejected/offline
    audit_comment = Column(Text, default="")
    auditor = Column(String(100), default="")
    audit_time = Column(DateTime, nullable=True)
    sensitive_words = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
