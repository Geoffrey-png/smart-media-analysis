from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import require_roles
from app.core.response import success
from app.db.database import get_db
from app.services.admin_service import admin_summary
from app.services.operation_log_service import list_operation_logs
from app.services.user_service import VALID_ROLES


router = APIRouter(prefix="/admin", tags=["管理员后台"])


@router.get("/summary")
def summary(db: Session = Depends(get_db), current_user: dict = Depends(require_roles("admin"))):
    return success(admin_summary(db))


@router.get("/logs")
def logs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = None,
    module: str | None = None,
    action: str | None = None,
    user_id: int | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin")),
):
    return success(list_operation_logs(db, page, page_size, keyword, module, action, user_id))


@router.get("/roles")
def roles(current_user: dict = Depends(require_roles("admin"))):
    labels = {
        "admin": "管理员",
        "editor": "编辑",
        "auditor": "审核员",
        "viewer": "观察者",
    }
    return success([{"value": role, "label": labels[role]} for role in sorted(VALID_ROLES)])
