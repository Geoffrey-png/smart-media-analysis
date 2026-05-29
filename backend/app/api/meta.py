from collections import Counter

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.response import success
from app.db.database import get_db
from app.models.category import Category
from app.models.content import Content
from app.models.tag import Tag
from app.services.content_service import split_tags


router = APIRouter(prefix="/meta", tags=["基础数据"])


@router.get("/categories")
def categories(db: Session = Depends(get_db)):
    rows = db.query(Category).order_by(Category.id).all()
    if rows:
        data = [
            {
                "id": row.id,
                "name": row.name,
                "description": row.description,
                "created_at": row.created_at.isoformat() if row.created_at else None,
            }
            for row in rows
        ]
    else:
        names = [row[0] for row in db.query(Content.category).distinct().all() if row[0]]
        data = [{"id": index + 1, "name": name, "description": ""} for index, name in enumerate(names)]
    return success(data)


@router.get("/tags")
def tags(db: Session = Depends(get_db)):
    rows = db.query(Tag).order_by(Tag.count.desc(), Tag.id).all()
    if rows:
        data = [{"id": row.id, "name": row.name, "count": row.count} for row in rows]
    else:
        counter = Counter()
        for content in db.query(Content).all():
            counter.update(split_tags(content.tags))
        data = [{"id": index + 1, "name": name, "count": count} for index, (name, count) in enumerate(counter.most_common())]
    return success(data)


@router.get("/options")
def options(db: Session = Depends(get_db)):
    category_res = categories(db)["data"]
    tag_res = tags(db)["data"]
    return success(
        {
            "categories": category_res,
            "tags": tag_res,
            "content_types": [
                {"label": "文章", "value": "article"},
                {"label": "视频", "value": "video"},
                {"label": "图片", "value": "image"},
            ],
        }
    )
