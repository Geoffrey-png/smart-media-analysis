from collections.abc import Callable

from fastapi import Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.services.auth_service import get_current_user


ROLE_LABELS = {
    "admin": "管理员",
    "editor": "编辑",
    "auditor": "审核员",
    "viewer": "观察者",
}


def require_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict:
    """要求请求携带有效 Bearer Token。"""

    return get_current_user(db, authorization)


def require_roles(*roles: str) -> Callable:
    """后端强制角色权限校验。前端隐藏菜单只是辅助，不能代替这里。"""

    allowed = set(roles)

    def dependency(current_user: dict = Depends(require_current_user)) -> dict:
      role = current_user.get("role") or "viewer"
      if role not in allowed:
          allowed_text = "、".join(ROLE_LABELS.get(item, item) for item in allowed)
          raise HTTPException(status_code=403, detail=f"权限不足，需要角色：{allowed_text}")
      return current_user

    return dependency


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",", 1)[0].strip()
    return request.client.host if request.client else ""
