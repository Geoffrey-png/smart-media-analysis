import json
from collections import Counter, defaultdict
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.behavior import UserBehavior
from app.models.content import Content
from app.models.recommendation_log import RecommendationLog
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.services.content_service import content_to_dict, join_tags, schema_to_dict, split_tags
from app.services.security_service import hash_password


VALID_ROLES = {"admin", "editor", "auditor", "viewer"}
VALID_USER_STATUS = {"active", "disabled"}

ACTION_WEIGHTS = {
    "view": 1,
    "like": 5,
    "favorite": 6,
    "comment": 4,
    "share": 4,
    "dislike": -6,
}


def _load_profile_vector(user: User) -> dict:
    try:
        return json.loads(user.profile_vector or "{}")
    except Exception:
        return {}


def user_to_dict(user: User) -> dict:
    return {
        "id": user.id,
        "username": user.username,
        "nickname": user.nickname,
        "role": getattr(user, "role", "viewer") or "viewer",
        "status": getattr(user, "status", "active") or "active",
        "age": user.age,
        "gender": user.gender,
        "city": user.city,
        "interests": split_tags(user.interests),
        "profile_vector": _load_profile_vector(user),
        "active_score": round(float(getattr(user, "active_score", 0) or 0), 2),
        "last_active_at": user.last_active_at.isoformat() if getattr(user, "last_active_at", None) else None,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "updated_at": user.updated_at.isoformat() if user.updated_at else None,
    }


def get_user_or_404(db: Session, user_id: int) -> User:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user


def list_users(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    role: str | None = None,
    status: str | None = None,
) -> dict:
    query = db.query(User)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter((User.username.like(like)) | (User.nickname.like(like)))
    if role:
        query = query.filter(User.role == role)
    if status:
        query = query.filter(User.status == status)
    total = query.count()
    items = query.order_by(User.id).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": [user_to_dict(item) for item in items], "total": total, "page": page, "page_size": page_size}


def create_user(db: Session, payload: UserCreate) -> dict:
    data = schema_to_dict(payload)
    raw_password = data.pop("password", None)
    legacy_password_hash = data.pop("password_hash", None)
    if raw_password:
        data["password_hash"] = hash_password(raw_password)
    elif legacy_password_hash:
        data["password_hash"] = hash_password(legacy_password_hash)
    else:
        raise HTTPException(status_code=400, detail="创建用户需要设置密码")
    data["interests"] = join_tags(data.get("interests"))
    if data.get("role") not in VALID_ROLES:
        data["role"] = "viewer"
    if data.get("status") not in VALID_USER_STATUS:
        data["status"] = "active"
    user = User(**data)
    db.add(user)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="用户名已存在") from exc
    db.refresh(user)
    return user_to_dict(user)


def update_user(db: Session, user_id: int, payload: UserUpdate) -> dict:
    user = get_user_or_404(db, user_id)
    data = schema_to_dict(payload, exclude_unset=True)
    raw_password = data.pop("password", None)
    legacy_password_hash = data.pop("password_hash", None)
    if raw_password:
        data["password_hash"] = hash_password(raw_password)
    elif legacy_password_hash:
        data["password_hash"] = hash_password(legacy_password_hash)
    if "interests" in data:
        data["interests"] = join_tags(data["interests"])
    if "role" in data and data["role"] not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"角色必须是：{', '.join(sorted(VALID_ROLES))}")
    if "status" in data and data["status"] not in VALID_USER_STATUS:
        raise HTTPException(status_code=400, detail=f"账号状态必须是：{', '.join(sorted(VALID_USER_STATUS))}")
    for key, value in data.items():
        setattr(user, key, value)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail="用户名已存在") from exc
    db.refresh(user)
    return user_to_dict(user)


def delete_user(db: Session, user_id: int) -> None:
    user = get_user_or_404(db, user_id)
    db.query(UserBehavior).filter(UserBehavior.user_id == user_id).delete(synchronize_session=False)
    db.query(RecommendationLog).filter(RecommendationLog.user_id == user_id).delete(synchronize_session=False)
    db.delete(user)
    db.commit()


def calculate_user_profile(db: Session, user_id: int) -> dict:
    user = get_user_or_404(db, user_id)
    behaviors = (
        db.query(UserBehavior, Content)
        .join(Content, UserBehavior.content_id == Content.id)
        .filter(UserBehavior.user_id == user_id)
        .order_by(UserBehavior.created_at.desc())
        .all()
    )

    tag_weights: defaultdict[str, float] = defaultdict(float)
    category_counter: Counter[str] = Counter()
    action_counter: Counter[str] = Counter()
    recent_contents = []
    active_score = 0.0

    for behavior, content in behaviors:
        weight = ACTION_WEIGHTS.get(behavior.action_type, 0)
        duration_boost = min((behavior.duration or 0) / 120, 2) if behavior.action_type == "view" else 0
        final_weight = weight + duration_boost
        active_score += max(final_weight, 0)
        action_counter[behavior.action_type] += 1
        category_counter[content.category or "未分类"] += 1
        for tag in split_tags(content.tags):
            tag_weights[tag] += final_weight
        if content.category:
            tag_weights[content.category] += final_weight * 0.6
        if len(recent_contents) < 10:
            recent_contents.append(
                {
                    "behavior": behavior.action_type,
                    "duration": behavior.duration,
                    "created_at": behavior.created_at.isoformat() if behavior.created_at else None,
                    "content": content_to_dict(content),
                }
            )

    for interest in split_tags(user.interests):
        tag_weights[interest] += 2

    sorted_tags = sorted(tag_weights.items(), key=lambda x: x[1], reverse=True)
    return {
        "user": user_to_dict(user),
        "interest_tags": [{"tag": tag, "weight": round(weight, 2)} for tag, weight in sorted_tags if weight > 0],
        "negative_tags": [{"tag": tag, "weight": round(weight, 2)} for tag, weight in sorted_tags if weight < 0],
        "category_distribution": [{"name": k, "value": v} for k, v in category_counter.most_common()],
        "behavior_stats": [{"name": k, "value": v} for k, v in action_counter.most_common()],
        "recent_contents": recent_contents,
        "active_score": round(active_score, 2),
    }


def refresh_user_profile_from_behaviors(db: Session, user_id: int, commit: bool = True) -> dict:
    user = get_user_or_404(db, user_id)
    profile = calculate_user_profile(db, user_id)
    top_tags = [item["tag"] for item in profile["interest_tags"][:12]]
    vector = {
        "interest_tags": profile["interest_tags"][:30],
        "negative_tags": profile["negative_tags"][:20],
        "category_distribution": profile["category_distribution"],
        "behavior_stats": profile["behavior_stats"],
        "updated_at": datetime.utcnow().isoformat(),
    }
    user.interests = join_tags(top_tags)
    user.profile_vector = json.dumps(vector, ensure_ascii=False)
    user.active_score = profile["active_score"]
    user.last_active_at = datetime.utcnow()
    if commit:
        db.commit()
        db.refresh(user)
    profile["user"] = user_to_dict(user)
    return profile


def build_user_profile(db: Session, user_id: int) -> dict:
    profile = calculate_user_profile(db, user_id)
    user = get_user_or_404(db, user_id)
    stored = _load_profile_vector(user)
    if stored and not profile["interest_tags"]:
        profile["interest_tags"] = stored.get("interest_tags", [])
        profile["negative_tags"] = stored.get("negative_tags", [])
        profile["category_distribution"] = stored.get("category_distribution", [])
        profile["behavior_stats"] = stored.get("behavior_stats", [])
    return profile
