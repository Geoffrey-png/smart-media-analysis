from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile

from app.api.deps import client_ip, require_roles
from app.core.config import settings
from app.core.response import success
from app.db.database import get_db
from app.services.operation_log_service import log_operation
from sqlalchemy.orm import Session


router = APIRouter(prefix="/uploads", tags=["文件上传"])

ALLOWED_SUFFIXES = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".mp4", ".mov", ".avi"}
MAX_SIZE = 50 * 1024 * 1024


@router.post("")
async def upload_file(
    request: Request,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: dict = Depends(require_roles("admin", "editor")),
):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in ALLOWED_SUFFIXES:
        raise HTTPException(status_code=400, detail="只支持图片和常见视频文件")

    data = await file.read()
    if len(data) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="文件不能超过 50MB")

    filename = f"{uuid4().hex}{suffix}"
    target = settings.UPLOAD_DIR / filename
    target.write_bytes(data)
    result = {
        "filename": filename,
        "url": f"/uploads/{filename}",
        "size": len(data),
        "content_type": file.content_type,
    }
    log_operation(db, current_user, "uploads", "upload_file", "file", filename, f"上传文件：{file.filename}", client_ip(request))
    return success(result, "上传成功")
