from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.operation_log import OperationLog


def operation_to_dict(log: OperationLog) -> dict:
    return {
        "id": log.id,
        "user_id": log.user_id,
        "username": log.username,
        "role": log.role,
        "module": log.module,
        "action": log.action,
        "target_type": log.target_type,
        "target_id": log.target_id,
        "detail": log.detail,
        "ip": log.ip,
        "created_at": log.created_at.isoformat() if log.created_at else None,
    }


def log_operation(
    db: Session,
    user: dict | None,
    module: str,
    action: str,
    target_type: str = "",
    target_id: str | int | None = "",
    detail: str = "",
    ip: str = "",
    commit: bool = True,
) -> OperationLog:
    log = OperationLog(
        user_id=(user or {}).get("id"),
        username=(user or {}).get("username") or "",
        role=(user or {}).get("role") or "",
        module=module,
        action=action,
        target_type=target_type,
        target_id=str(target_id or ""),
        detail=detail[:1000] if detail else "",
        ip=ip or "",
    )
    db.add(log)
    if commit:
        db.commit()
        db.refresh(log)
    return log


def list_operation_logs(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    module: str | None = None,
    action: str | None = None,
    user_id: int | None = None,
) -> dict:
    query = db.query(OperationLog)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter(
            or_(
                OperationLog.username.like(like),
                OperationLog.module.like(like),
                OperationLog.action.like(like),
                OperationLog.detail.like(like),
                OperationLog.target_id.like(like),
            )
        )
    if module:
        query = query.filter(OperationLog.module == module)
    if action:
        query = query.filter(OperationLog.action == action)
    if user_id:
        query = query.filter(OperationLog.user_id == user_id)
    total = query.count()
    items = (
        query.order_by(OperationLog.created_at.desc(), OperationLog.id.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return {"items": [operation_to_dict(item) for item in items], "total": total, "page": page, "page_size": page_size}
