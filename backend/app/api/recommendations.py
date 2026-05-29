from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.algorithms import recommender
from app.api.deps import require_current_user, require_roles
from app.core.response import success
from app.db.database import get_db
from app.schemas.recommendation import RecommendationClick
from app.services.recommendation_log_service import (
    log_recommendation_click,
    log_recommendations,
    recommendation_analytics,
)


router = APIRouter(prefix="/recommendations", tags=["推荐系统"])


@router.get("/hot")
def hot_recommendations(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    items = recommender.recommend_hot(db, limit)
    log_recommendations(db, items, user_id=None, scene="hot", action="exposure")
    return success(items)


@router.get("/user/{user_id}")
def user_recommendations(
    user_id: int,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_current_user),
):
    if current_user.get("role") not in {"admin", "editor"} and current_user.get("id") != user_id:
        raise HTTPException(status_code=403, detail="只能查看自己的推荐")
    items = recommender.recommend_for_user(db, user_id, limit)
    log_recommendations(db, items, user_id=user_id, scene="user", action="exposure")
    return success(items)


@router.get("/content/{content_id}")
def content_recommendations(content_id: int, limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    items = recommender.recommend_similar_content(db, content_id, limit)
    log_recommendations(db, items, user_id=None, scene=f"content:{content_id}", action="exposure")
    return success(items)


@router.get("/mixed")
def mixed_recommendations(
    user_id: int | None = None,
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_current_user),
):
    target_user_id = user_id or current_user.get("id")
    if current_user.get("role") not in {"admin", "editor"} and target_user_id != current_user.get("id"):
        raise HTTPException(status_code=403, detail="只能查看自己的推荐")
    items = recommender.recommend_mixed(db, target_user_id, limit)
    log_recommendations(db, items, user_id=target_user_id, scene="mixed", action="exposure")
    return success(items)


@router.get("/analytics/summary")
def analytics_summary(db: Session = Depends(get_db), current_user: dict = Depends(require_roles("admin", "editor", "auditor"))):
    return success(recommendation_analytics(db))


@router.post("/click")
def recommendation_click(
    payload: RecommendationClick,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_current_user),
):
    user_id = payload.user_id or current_user["id"]
    if current_user.get("role") != "admin" and user_id != current_user.get("id"):
        raise HTTPException(status_code=403, detail="只能记录自己的推荐点击")
    data = log_recommendation_click(
        db,
        content_id=payload.content_id,
        user_id=user_id,
        scene=payload.scene,
        recommend_score=payload.recommend_score,
        reason=payload.reason,
    )
    return success(data, "推荐点击已记录")
