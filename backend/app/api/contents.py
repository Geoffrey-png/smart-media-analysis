from fastapi import APIRouter, Depends, Query, Request
from sqlalchemy.orm import Session

from app.api.deps import client_ip, require_current_user, require_roles
from app.core.response import success
from app.db.database import get_db
from app.schemas.content import ContentAudit, ContentCreate, ContentUpdate
from app.services import content_service
from app.services.operation_log_service import log_operation


router = APIRouter(prefix="/contents", tags=["内容管理"])


@router.get("")
def list_contents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    keyword: str | None = None,
    category: str | None = None,
    content_type: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
):
    data = content_service.list_contents(db, page, page_size, keyword, category, content_type, status)
    return success(data)


@router.get("/hot")
def hot_contents(limit: int = Query(10, ge=1, le=50), db: Session = Depends(get_db)):
    return success(content_service.hot_contents(db, limit))


@router.get("/audit/pending")
def pending_contents(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin", "auditor")),
):
    data = content_service.list_contents(db, page, page_size, status="pending")
    return success(data)


@router.get("/{content_id}")
def content_detail(content_id: int, db: Session = Depends(get_db)):
    content = content_service.get_content_or_404(db, content_id)
    return success(content_service.content_to_dict(content))


@router.post("")
def create_content(
    payload: ContentCreate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin", "editor")),
):
    data = content_service.create_content(db, payload)
    log_operation(db, current_user, "contents", "create_content", "content", data["id"], f"创建内容：{data['title']}", client_ip(request))
    return success(data, "内容创建成功")


@router.put("/{content_id}")
def update_content(
    content_id: int,
    payload: ContentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin", "editor")),
):
    data = content_service.update_content(db, content_id, payload)
    log_operation(db, current_user, "contents", "update_content", "content", content_id, f"更新内容：{data['title']}", client_ip(request))
    return success(data, "内容更新成功")


@router.delete("/{content_id}")
def delete_content(
    content_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin")),
):
    content = content_service.get_content_or_404(db, content_id)
    title = content.title
    content_service.delete_content(db, content_id)
    log_operation(db, current_user, "contents", "delete_content", "content", content_id, f"删除内容：{title}", client_ip(request))
    return success(None, "内容删除成功")


@router.post("/{content_id}/analyze")
def analyze_content(
    content_id: int,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin", "editor")),
):
    data = content_service.analyze_content(db, content_id)
    log_operation(db, current_user, "contents", "analyze_content", "content", content_id, f"分析内容：{data['title']}", client_ip(request))
    return success(data, "内容分析完成")


@router.post("/{content_id}/audit")
def audit_content(
    content_id: int,
    payload: ContentAudit,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin", "auditor")),
):
    auditor = current_user.get("nickname") or current_user.get("username") or ""
    data = content_service.audit_content(db, content_id, payload.status, payload.audit_comment, auditor)
    log_operation(db, current_user, "contents", "audit_content", "content", content_id, f"审核内容为 {payload.status}：{data['title']}", client_ip(request))
    return success(data, "审核操作完成")
