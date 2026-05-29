from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.core.response import success
from app.db.database import get_db
from app.schemas.auth import LoginRequest
from app.services import auth_service


router = APIRouter(prefix="/auth", tags=["登录认证"])


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    return success(auth_service.login(db, payload.username, payload.password), "登录成功")


@router.get("/me")
def current_user(authorization: str | None = Header(default=None), db: Session = Depends(get_db)):
    return success(auth_service.get_current_user(db, authorization))

