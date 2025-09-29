"""Pydantic схемы для администраторов."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class AdminLoginRequest(BaseModel):
    """Схема запроса аутентификации для POST /api/v1/admin/auth/login."""

    username: str = Field(
        ..., min_length=3, max_length=50, description="Имя пользователя"
    )
    password: str = Field(..., min_length=6, description="Пароль")

    model_config = ConfigDict(
        json_schema_extra={"example": {"username": "admin", "password": "admin123"}}
    )


class AdminRefreshRequest(BaseModel):
    """Схема запроса обновления токена для POST /api/v1/admin/auth/refresh."""

    refresh_token: str = Field(..., description="Refresh токен")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}
        }
    )


class AdminLoginResponse(BaseModel):
    """Схема ответа аутентификации для POST /api/v1/admin/auth/login."""

    access_token: str = Field(..., description="JWT токен доступа")
    refresh_token: str = Field(..., description="Refresh токен")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни токена в секундах")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
            }
        }
    )


class AdminRefreshResponse(BaseModel):
    """Схема ответа обновления токена для POST /api/v1/admin/auth/refresh."""

    access_token: str = Field(..., description="Новый JWT токен доступа")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни токена в секундах")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
            }
        }
    )
