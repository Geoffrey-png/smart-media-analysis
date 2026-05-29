from datetime import datetime

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.models.behavior import UserBehavior
from app.models.content import Content
from app.models.operation_log import OperationLog
from app.models.recommendation_log import RecommendationLog
from app.models.user import User


def admin_summary(db: Session) -> dict:
    today = datetime.utcnow().date()
    role_rows = db.query(User.role, func.count(User.id)).group_by(User.role).all()
    user_status_rows = db.query(User.status, func.count(User.id)).group_by(User.status).all()
    status_rows = db.query(Content.status, func.count(Content.id)).group_by(Content.status).all()
    source_rows = (
        db.query(Content.source_name, func.count(Content.id))
        .filter(Content.source_name != "")
        .group_by(Content.source_name)
        .order_by(func.count(Content.id).desc())
        .limit(8)
        .all()
    )

    return {
        "user_count": db.query(User).count(),
        "active_user_count": db.query(User).filter(User.status == "active").count(),
        "disabled_user_count": db.query(User).filter(User.status == "disabled").count(),
        "content_count": db.query(Content).count(),
        "news_count": db.query(Content).filter(Content.source_url != "").count(),
        "pending_audit_count": db.query(Content).filter(Content.status == "pending").count(),
        "behavior_count": db.query(UserBehavior).count(),
        "recommendation_log_count": db.query(RecommendationLog).count(),
        "operation_log_count": db.query(OperationLog).count(),
        "today_operation_count": db.query(OperationLog).filter(func.date(OperationLog.created_at) == str(today)).count(),
        "role_distribution": [{"name": role or "viewer", "value": count} for role, count in role_rows],
        "user_status_distribution": [{"name": status or "active", "value": count} for status, count in user_status_rows],
        "content_status_distribution": [{"name": status or "unknown", "value": count} for status, count in status_rows],
        "news_source_distribution": [{"name": name or "未知来源", "value": count} for name, count in source_rows],
        "top_active_users": [
            {
                "id": user.id,
                "username": user.username,
                "nickname": user.nickname,
                "role": user.role or "viewer",
                "status": getattr(user, "status", "active") or "active",
                "active_score": round(float(user.active_score or 0), 2),
            }
            for user in db.query(User).order_by(desc(User.active_score), desc(User.id)).limit(6).all()
        ],
        "recent_operations": [
            {
                "id": item.id,
                "username": item.username,
                "role": item.role,
                "module": item.module,
                "action": item.action,
                "detail": item.detail,
                "created_at": item.created_at.isoformat() if item.created_at else None,
            }
            for item in db.query(OperationLog).order_by(desc(OperationLog.created_at), desc(OperationLog.id)).limit(8).all()
        ],
    }
