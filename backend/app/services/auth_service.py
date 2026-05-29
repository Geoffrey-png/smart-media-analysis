from datetime import datetime, timedelta

from fastapi import HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.user import User
from app.services.security_service import verify_password
from app.services.user_service import user_to_dict


def create_access_token(user: User) -> str:
    """生成演示版 JWT。"""

    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": str(user.id),
        "username": user.username,
        "exp": expire,
    }
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def verify_access_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="登录状态无效")
        return int(user_id)
    except JWTError as exc:
        raise HTTPException(status_code=401, detail="登录状态已过期，请重新登录") from exc


def login(db: Session, username: str, password: str) -> dict:
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if not verify_password(password, user.password_hash or ""):
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if getattr(user, "status", "active") == "disabled":
        raise HTTPException(status_code=403, detail="账号已被管理员禁用")

    token = create_access_token(user)
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": user_to_dict(user),
    }


def get_current_user(db: Session, authorization: str | None) -> dict:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="请先登录")
    token = authorization.split(" ", 1)[1].strip()
    user_id = verify_access_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在")
    if getattr(user, "status", "active") == "disabled":
        raise HTTPException(status_code=403, detail="账号已被管理员禁用")
    return user_to_dict(user)
