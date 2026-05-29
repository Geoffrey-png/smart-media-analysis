from typing import Any


def success(data: Any = None, message: str = "success") -> dict:
    """统一成功响应。"""

    return {"code": 0, "message": message, "data": data}


def fail(message: str = "error", code: int = 400, data: Any = None) -> dict:
    """统一失败响应。"""

    return {"code": code, "message": message, "data": data}


def paginate(items: list, total: int, page: int, page_size: int) -> dict:
    """统一分页结构。"""

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }

