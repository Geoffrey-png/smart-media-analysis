from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.content import Content
from app.models.recommendation_log import RecommendationLog
from app.services.behavior_service import add_behavior_event


def log_recommendations(
    db: Session,
    items: list[dict],
    user_id: int | None,
    scene: str,
    action: str = "exposure",
) -> None:
    """记录推荐曝光/点击日志。"""

    if not items:
        return
    logs = [
        RecommendationLog(
            user_id=user_id,
            content_id=item["id"],
            scene=scene,
            action=action,
            recommend_score=float(item.get("recommend_score") or 0),
            reason=item.get("reason") or "",
            created_at=datetime.utcnow(),
        )
        for item in items
        if item.get("id")
    ]
    db.add_all(logs)
    db.commit()


def log_recommendation_click(
    db: Session,
    content_id: int,
    user_id: int | None,
    scene: str,
    recommend_score: float = 0,
    reason: str = "",
) -> dict:
    log = RecommendationLog(
        user_id=user_id,
        content_id=content_id,
        scene=scene,
        action="click",
        recommend_score=recommend_score,
        reason=reason,
        created_at=datetime.utcnow(),
    )
    db.add(log)

    # 点击推荐位本质上也是一次浏览行为，用它同步更新内容热度和用户画像。
    if user_id:
        add_behavior_event(db, user_id=user_id, content_id=content_id, action_type="view", duration=0, commit=False)

    db.commit()
    db.refresh(log)
    return {
        "id": log.id,
        "user_id": log.user_id,
        "content_id": log.content_id,
        "scene": log.scene,
        "action": log.action,
        "recommend_score": log.recommend_score,
        "reason": log.reason,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    }


def recommendation_analytics(db: Session) -> dict:
    """推荐效果分析。"""

    exposure_count = db.query(RecommendationLog).filter(RecommendationLog.action == "exposure").count()
    click_count = db.query(RecommendationLog).filter(RecommendationLog.action == "click").count()
    ctr = round(click_count / exposure_count * 100, 2) if exposure_count else 0

    scene_rows = (
        db.query(RecommendationLog.scene, RecommendationLog.action, func.count(RecommendationLog.id))
        .group_by(RecommendationLog.scene, RecommendationLog.action)
        .all()
    )
    scene_map: dict[str, dict] = {}
    for scene, action, count in scene_rows:
        key = scene or "unknown"
        item = scene_map.setdefault(key, {"scene": key, "exposure": 0, "click": 0, "ctr": 0})
        item[action] = count
    for item in scene_map.values():
        item["ctr"] = round(item["click"] / item["exposure"] * 100, 2) if item["exposure"] else 0

    top_rows = (
        db.query(Content.id, Content.title, Content.category, func.count(RecommendationLog.id).label("clicks"))
        .join(RecommendationLog, RecommendationLog.content_id == Content.id)
        .filter(RecommendationLog.action == "click")
        .group_by(Content.id, Content.title, Content.category)
        .order_by(func.count(RecommendationLog.id).desc())
        .limit(10)
        .all()
    )
    trend_rows = (
        db.query(func.date(RecommendationLog.created_at), RecommendationLog.action, func.count(RecommendationLog.id))
        .group_by(func.date(RecommendationLog.created_at), RecommendationLog.action)
        .order_by(func.date(RecommendationLog.created_at))
        .all()
    )
    trend_map: dict[str, dict] = {}
    for day, action, count in trend_rows:
        key = str(day)
        item = trend_map.setdefault(key, {"date": key, "exposure": 0, "click": 0})
        item[action] = count

    return {
        "exposure_count": exposure_count,
        "click_count": click_count,
        "ctr": ctr,
        "scene_stats": list(scene_map.values()),
        "top_clicked_contents": [
            {"id": row.id, "title": row.title, "category": row.category, "clicks": row.clicks}
            for row in top_rows
        ],
        "trend": list(trend_map.values()),
    }
