from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str
    exp: int


class AdminUserBase(BaseModel):
    username: str


class AdminUserResponse(AdminUserBase):
    id: int
    role: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    user_id: int | None = None
    username: Optional[str] = None
    fullname: Optional[str] = None
    avatar_url: Optional[str] = None

    class Config:
        from_attributes = True


class ArticleRatingResponse(BaseModel):
    id: int
    fullname: Optional[str] = None
    article_name: str
    rating: int
    created_at: datetime

    class Config:
        from_attributes = True


class ArticleRatingSummaryItem(BaseModel):
    article_name: str
    ratings_count: int
    avg_rating: float

