from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.algorithms.content_analyzer import calculate_heat_score, calculate_quality_score
from app.models.behavior import UserBehavior
from app.models.content import Content
from app.models.user import User
from app.schemas.behavior import BehaviorCreate
from app.services.user_service import refresh_user_profile_from_behaviors


VALID_ACTIONS = {"view", "like", "favorite", "comment", "share", "dislike"}


def behavior_to_dict(behavior: UserBehavior) -> dict:
    return {
        "id": behavior.id,
        "user_id": behavior.user_id,
        "content_id": behavior.content_id,
        "action_type": behavior.action_type,
        "duration": behavior.duration,
        "created_at": behavior.created_at.isoformat() if behavior.created_at else None,
    }


def _update_content_stats(content: Content, action_type: str) -> None:
    if action_type == "view":
        content.view_count += 1
    elif action_type == "like":
        content.like_count += 1
    elif action_type == "favorite":
        content.favorite_count += 1
    elif action_type == "comment":
        content.comment_count += 1

    content.heat_score = calculate_heat_score(
        content.view_count,
        content.like_count,
        content.favorite_count,
        content.comment_count,
    )
    content.quality_score = calculate_quality_score(content)


def create_behavior(db: Session, payload: BehaviorCreate) -> dict:
    if payload.action_type not in VALID_ACTIONS:
        raise HTTPException(status_code=400, detail=f"行为类型必须是：{', '.join(sorted(VALID_ACTIONS))}")
    user = db.query(User).filter(User.id == payload.user_id).first()
    content = db.query(Content).filter(Content.id == payload.content_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")

    data = payload.model_dump() if hasattr(payload, "model_dump") else payload.dict()
    behavior = UserBehavior(**data)
    behavior.created_at = datetime.utcnow()
    db.add(behavior)
    _update_content_stats(content, payload.action_type)

    db.flush()
    profile = refresh_user_profile_from_behaviors(db, payload.user_id, commit=False)
    db.commit()
    db.refresh(behavior)
    result = behavior_to_dict(behavior)
    result["profile"] = {
        "interest_tags": profile.get("interest_tags", [])[:10],
        "active_score": profile.get("active_score", 0),
    }
    return result


def add_behavior_event(
    db: Session,
    user_id: int,
    content_id: int,
    action_type: str,
    duration: int = 0,
    commit: bool = True,
) -> UserBehavior:
    if action_type not in VALID_ACTIONS:
        raise HTTPException(status_code=400, detail=f"行为类型必须是：{', '.join(sorted(VALID_ACTIONS))}")
    content = db.query(Content).filter(Content.id == content_id).first()
    if not content:
        raise HTTPException(status_code=404, detail="内容不存在")
    if user_id and not db.query(User).filter(User.id == user_id).first():
        raise HTTPException(status_code=404, detail="用户不存在")

    behavior = UserBehavior(
        user_id=user_id,
        content_id=content_id,
        action_type=action_type,
        duration=duration,
        created_at=datetime.utcnow(),
    )
    db.add(behavior)
    _update_content_stats(content, action_type)
    db.flush()
    if user_id:
        refresh_user_profile_from_behaviors(db, user_id, commit=False)
    if commit:
        db.commit()
        db.refresh(behavior)
    return behavior


def list_behaviors(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    user_id: int | None = None,
    content_id: int | None = None,
    action_type: str | None = None,
) -> dict:
    query = db.query(UserBehavior)
    if user_id:
        query = query.filter(UserBehavior.user_id == user_id)
    if content_id:
        query = query.filter(UserBehavior.content_id == content_id)
    if action_type:
        query = query.filter(UserBehavior.action_type == action_type)
    total = query.count()
    items = (
        query.order_by(UserBehavior.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"items": [behavior_to_dict(item) for item in items], "total": total, "page": page, "page_size": page_size}
