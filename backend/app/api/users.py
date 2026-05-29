from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import client_ip, require_current_user, require_roles
from app.core.response import success
from app.db.database import get_db
from app.schemas.user import UserCreate, UserUpdate
from app.services import user_service
from app.services.operation_log_service import log_operation


router = APIRouter(prefix="/users", tags=["用户管理"])


@router.get("")
def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str | None = None,
    role: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin")),
):
    return success(user_service.list_users(db, page, page_size, keyword, role, status))


@router.get("/{user_id}")
def user_detail(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin")),
):
    return success(user_service.user_to_dict(user_service.get_user_or_404(db, user_id)))


@router.post("")
def create_user(
    payload: UserCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin")),
):
    data = user_service.create_user(db, payload)
    log_operation(db, current_user, "users", "create_user", "user", data["id"], f"创建用户：{data['username']}", client_ip(request))
    return success(data, "用户创建成功")


@router.put("/{user_id}")
def update_user(
    user_id: int,
    payload: UserUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin")),
):
    if user_id == current_user.get("id") and payload.status == "disabled":
        raise HTTPException(status_code=400, detail="不能禁用当前登录管理员")
    if user_id == current_user.get("id") and payload.role and payload.role != "admin":
        raise HTTPException(status_code=400, detail="不能降低当前登录管理员的角色")
    data = user_service.update_user(db, user_id, payload)
    log_operation(db, current_user, "users", "update_user", "user", user_id, f"更新用户：{data['username']}", client_ip(request))
    return success(data, "用户更新成功")


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin")),
):
    if user_id == current_user.get("id"):
        raise HTTPException(status_code=400, detail="不能删除当前登录管理员")
    target = user_service.get_user_or_404(db, user_id)
    username = target.username
    user_service.delete_user(db, user_id)
    log_operation(db, current_user, "users", "delete_user", "user", user_id, f"删除用户：{username}", client_ip(request))
    return success(None, "用户删除成功")


@router.get("/{user_id}/profile")
def user_profile(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_current_user),
):
    if current_user.get("role") != "admin" and current_user.get("id") != user_id:
        raise HTTPException(status_code=403, detail="只能查看自己的画像")
    return success(user_service.build_user_profile(db, user_id))
