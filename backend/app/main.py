from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api import api_router
from app.core.config import settings
from app.core.response import fail, success
from app.db.database import Base, engine, ensure_sqlite_schema
from app import models  # noqa: F401 - 确保模型被 SQLAlchemy 注册


def create_app() -> FastAPI:
    app = FastAPI(
        title=settings.APP_NAME,
        description="基于 Python FastAPI 的智能传媒内容分析与推荐系统后端 API",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.on_event("startup")
    def on_startup():
        Base.metadata.create_all(bind=engine)
        ensure_sqlite_schema()
        _auto_seed_if_empty()

    def _auto_seed_if_empty():
        """数据库为空时自动播种演示数据（安全：不覆盖已有数据）。"""
        try:
            from app.db.database import SessionLocal
            from app.db.seed import seed_if_empty

            db = SessionLocal()
            try:
                if seed_if_empty(db):
                    print("[startup] 数据库为空，已自动播种演示数据。")
            finally:
                db.close()
        except Exception:
            pass  # 播种失败不影响服务启动

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        return JSONResponse(
            status_code=exc.status_code,
            content=fail(getattr(exc, "detail", "请求错误"), exc.status_code),
        )

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=fail("参数校验失败", 422, exc.errors()),
        )

    @app.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        return JSONResponse(status_code=500, content=fail(str(exc), 500))

    @app.get("/")
    def root():
        return success(
            {
                "name": settings.APP_NAME,
                "docs": "/docs",
                "api_prefix": "/api",
            }
        )

    app.include_router(api_router)
    app.mount("/uploads", StaticFiles(directory=str(settings.UPLOAD_DIR)), name="uploads")
    return app


app = create_app()
