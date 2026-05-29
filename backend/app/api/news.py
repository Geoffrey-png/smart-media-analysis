from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.api.deps import client_ip, require_roles
from app.core.response import success
from app.db.database import get_db
from app.schemas.news import NewsImportRequest
from app.services.news_crawler_service import import_news, source_list
from app.services.operation_log_service import log_operation


router = APIRouter(prefix="/news", tags=["新闻采集"])


@router.get("/sources")
def news_sources():
    return success(source_list())


@router.post("/import")
def import_news_endpoint(
    payload: NewsImportRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin", "editor")),
):
    data = import_news(
        db,
        source_key=payload.source_key,
        limit=payload.limit,
        fetch_full_text=payload.fetch_full_text,
        custom_url=payload.custom_url,
        custom_name=payload.custom_name,
    )
    log_operation(
        db,
        current_user,
        "news",
        "import_news",
        "source",
        payload.source_key,
        f"采集新闻：新增 {data['imported_count']} 条，跳过 {data['skipped_count']} 条",
        client_ip(request),
    )
    return success(data, f"新闻采集完成，新增 {data['imported_count']} 条")
