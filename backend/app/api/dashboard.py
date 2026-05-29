from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import success
from app.db.database import get_db
from app.services.dashboard_service import dashboard_summary


router = APIRouter(prefix="/dashboard", tags=["数据统计"])


@router.get("/summary")
def summary(db: Session = Depends(get_db)):
    return success(dashboard_summary(db))

