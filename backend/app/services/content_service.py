from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import desc, or_
from sqlalchemy.orm import Session

from app.algorithms.content_analyzer import (
    analyze_content_payload,
    calculate_heat_score,
    calculate_quality_score,
)
from app.core.response import paginate
from app.models.behavior import UserBehavior
from app.models.content import Content
from app.models.recommendation_log import RecommendationLog
from app.schemas.content import ContentCreate, ContentUpdate


def schema_to_dict(schema, exclude_unset: bool = False) -> dict:
    if hasattr(schema, "model_dump"):
        return schema.model_dump(exclude_unset=exclude_unset)
    return schema.dict(exclude_unset=exclude_unset)


def split_tags(tags: str | list[str] | None) -> list[str]:
    if not tags:
        return []
    if isinstance(tags, list):
        return [str(t).strip() for t in tags if str(t).strip()]
    normalized = (
        str(tags)
        .replace("，", ",")
        .replace("、", ",")
        .replace("；", ",")
        .replace(";", ",")
        .replace("|", ",")
    )
    return [t.strip() for t in normalized.split(",") if t.strip()]


def join_tags(tags: str | list[str] | None) -> str:
    return ",".join(split_tags(tags))


def content_to_dict(content: Content) -> dict:
    return {
        "id": content.id,
        "title": content.title,
        "summary": content.summary,
        "content": content.content,
        "author": content.author,
        "category": content.category,
        "tags": split_tags(content.tags),
        "cover_url": content.cover_url,
        "source_name": getattr(content, "source_name", "") or "",
        "source_url": getattr(content, "source_url", "") or "",
        "content_type": content.content_type,
        "publish_time": content.publish_time.isoformat() if content.publish_time else None,
        "view_count": content.view_count,
        "like_count": content.like_count,
        "favorite_count": content.favorite_count,
        "comment_count": content.comment_count,
        "heat_score": content.heat_score,
        "quality_score": content.quality_score,
        "sentiment": content.sentiment,
        "status": getattr(content, "status", "published") or "published",
        "audit_comment": getattr(content, "audit_comment", "") or "",
        "auditor": getattr(content, "auditor", "") or "",
        "audit_time": content.audit_time.isoformat() if getattr(content, "audit_time", None) else None,
        "sensitive_words": split_tags(getattr(content, "sensitive_words", "") or ""),
        "created_at": content.created_at.isoformat() if content.created_at else None,
        "updated_at": content.updated_at.isoformat() if content.updated_at else None,
    }


def get_content_or_404(db: Session, content_id: int) -> Content:
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")
    return content


def list_contents(
    db: Session,
    page: int = 1,
    page_size: int = 10,
    keyword: str | None = None,
    category: str | None = None,
    content_type: str | None = None,
    status: str | None = None,
) -> dict:
    query = db.query(Content)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            or_(
                Content.title.like(like),
                Content.content.like(like),
                Content.tags.like(like),
                Content.source_name.like(like),
            )
        )
    if category:
        query = query.filter(Content.category == category)
    if content_type:
        query = query.filter(Content.content_type == content_type)
    if status:
        query = query.filter(Content.status == status)

    total = query.count()
    items = (
        query.order_by(desc(Content.publish_time), desc(Content.id))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return paginate([content_to_dict(item) for item in items], total, page, page_size)


def _apply_analysis(content: Content, force_category: bool = False) -> None:
    analysis = analyze_content_payload(content.title, content.content, content)
    if not content.summary:
        content.summary = analysis["summary"]
    if force_category or not content.category or content.category == "未分类":
        content.category = analysis["category"]
    if not content.tags:
        content.tags = join_tags(analysis["keywords"])
    content.sentiment = analysis["sentiment"]
    content.sensitive_words = join_tags(analysis["sensitive_words"])
    if analysis["sensitive_words"] and content.status == "published":
        content.status = "pending"
    content.heat_score = analysis["heat_score"]
    content.quality_score = calculate_quality_score(content)


def create_content(db: Session, payload: ContentCreate) -> dict:
    data = schema_to_dict(payload)
    data["tags"] = join_tags(data.get("tags"))
    if not data.get("publish_time"):
        data["publish_time"] = datetime.utcnow()

    content = Content(**data)
    _apply_analysis(content)

    db.add(content)
    db.commit()
    db.refresh(content)
    return content_to_dict(content)


def update_content(db: Session, content_id: int, payload: ContentUpdate) -> dict:
    content = get_content_or_404(db, content_id)
    data = schema_to_dict(payload, exclude_unset=True)
    if "tags" in data:
        data["tags"] = join_tags(data["tags"])
    if "sensitive_words" in data:
        data["sensitive_words"] = join_tags(data["sensitive_words"])
    for key, value in data.items():
        setattr(content, key, value)

    content.heat_score = calculate_heat_score(
        content.view_count,
        content.like_count,
        content.favorite_count,
        content.comment_count,
    )
    content.quality_score = calculate_quality_score(content)
    db.commit()
    db.refresh(content)
    return content_to_dict(content)


def delete_content(db: Session, content_id: int) -> None:
    content = get_content_or_404(db, content_id)
    db.query(UserBehavior).filter(UserBehavior.content_id == content_id).delete(synchronize_session=False)
    db.query(RecommendationLog).filter(RecommendationLog.content_id == content_id).delete(synchronize_session=False)
    db.delete(content)
    db.commit()


def analyze_content(db: Session, content_id: int) -> dict:
    content = get_content_or_404(db, content_id)
    _apply_analysis(content, force_category=True)
    db.commit()
    db.refresh(content)
    result = content_to_dict(content)
    result["analysis"] = analyze_content_payload(content.title, content.content, content)
    return result


def audit_content(db: Session, content_id: int, status: str, audit_comment: str, auditor: str = "") -> dict:
    valid_status = {"draft", "pending", "published", "rejected", "offline"}
    if status not in valid_status:
        raise HTTPException(status_code=400, detail=f"状态必须是：{', '.join(sorted(valid_status))}")
    content = get_content_or_404(db, content_id)
    content.status = status
    content.audit_comment = audit_comment or ""
    content.auditor = auditor or ""
    content.audit_time = datetime.utcnow()
    db.commit()
    db.refresh(content)
    return content_to_dict(content)


def hot_contents(db: Session, limit: int = 10) -> list[dict]:
    items = (
        db.query(Content)
        .filter(Content.status == "published")
        .order_by(desc(Content.heat_score), desc(Content.view_count), desc(Content.publish_time))
        .limit(limit)
        .all()
    )
    return [content_to_dict(item) for item in items]
