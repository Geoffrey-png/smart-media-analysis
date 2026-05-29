from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ContentCreate(BaseModel):
    title: str
    content: str
    summary: str = ""
    author: str = "系统编辑"
    category: str = "未分类"
    tags: list[str] = Field(default_factory=list)
    cover_url: str = ""
    source_name: str = ""
    source_url: str = ""
    content_type: str = "article"
    status: str = "published"
    publish_time: Optional[datetime] = None
    view_count: int = 0
    like_count: int = 0
    favorite_count: int = 0
    comment_count: int = 0


class ContentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[list[str]] = None
    cover_url: Optional[str] = None
    source_name: Optional[str] = None
    source_url: Optional[str] = None
    content_type: Optional[str] = None
    publish_time: Optional[datetime] = None
    view_count: Optional[int] = None
    like_count: Optional[int] = None
    favorite_count: Optional[int] = None
    comment_count: Optional[int] = None
    heat_score: Optional[float] = None
    quality_score: Optional[float] = None
    sentiment: Optional[str] = None
    status: Optional[str] = None
    audit_comment: Optional[str] = None
    auditor: Optional[str] = None
    audit_time: Optional[datetime] = None
    sensitive_words: Optional[list[str]] = None


class ContentAudit(BaseModel):
    status: str
    audit_comment: str = ""
