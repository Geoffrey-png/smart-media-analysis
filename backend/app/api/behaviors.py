from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.deps import require_current_user, require_roles
from app.core.response import success
from app.db.database import get_db
from app.schemas.behavior import BehaviorCreate
from app.services import behavior_service


router = APIRouter(prefix="/behaviors", tags=["行为日志"])


@router.get("")
def list_behaviors(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_id: int | None = None,
    content_id: int | None = None,
    action_type: str | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin", "editor", "auditor")),
):
    return success(behavior_service.list_behaviors(db, page, page_size, user_id, content_id, action_type))


@router.post("")
def create_behavior(
    payload: BehaviorCreate,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_current_user),
):
    if current_user.get("role") != "admin" and payload.user_id != current_user.get("id"):
        raise HTTPException(status_code=403, detail="只能记录自己的行为")
    return success(behavior_service.create_behavior(db, payload), "行为记录成功")
