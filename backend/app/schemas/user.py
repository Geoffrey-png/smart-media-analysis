from typing import Optional

from pydantic import BaseModel, Field


class UserCreate(BaseModel):
    username: str
    nickname: str = ""
    password: str
    password_hash: str | None = None
    role: str = "viewer"
    status: str = "active"
    age: int = 0
    gender: str = "unknown"
    city: str = ""
    interests: list[str] = Field(default_factory=list)


class UserUpdate(BaseModel):
    username: Optional[str] = None
    nickname: Optional[str] = None
    password: Optional[str] = None
    password_hash: Optional[str] = None
    role: Optional[str] = None
    status: Optional[str] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    city: Optional[str] = None
    interests: Optional[list[str]] = None
