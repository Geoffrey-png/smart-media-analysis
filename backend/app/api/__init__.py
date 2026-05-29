from fastapi import APIRouter

from app.api import admin, auth, behaviors, contents, dashboard, meta, news, recommendations, uploads, users


api_router = APIRouter(prefix="/api")
api_router.include_router(auth.router)
api_router.include_router(admin.router)
api_router.include_router(contents.router)
api_router.include_router(users.router)
api_router.include_router(behaviors.router)
api_router.include_router(recommendations.router)
api_router.include_router(dashboard.router)
api_router.include_router(meta.router)
api_router.include_router(uploads.router)
api_router.include_router(news.router)
