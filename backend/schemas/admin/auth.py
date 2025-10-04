"""Pydantic схемы для администраторов."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from backend.models.enums import AdminRole


class AdminLoginRequest(BaseModel):
    """Схема запроса аутентификации для POST /api/v1/admin/auth/login."""

    login: str = Field(..., min_length=3, max_length=255, description="Email или username для входа")
    password: str = Field(..., min_length=6, max_length=100, description="Пароль")

    model_config = ConfigDict(json_schema_extra={"example": {"login": "admin@example.com", "password": "admin123"}})


class AdminRefreshRequest(BaseModel):
    """Схема запроса обновления токена для POST /api/v1/admin/auth/refresh."""

    refresh_token: str = Field(..., description="Refresh токен")

    model_config = ConfigDict(
        json_schema_extra={"example": {"refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."}}
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


class AdminMeResponse(BaseModel):
    """Схема ответа информации о текущем администраторе для GET /api/v1/admin/auth/me."""

    id: int = Field(..., description="ID администратора")
    username: str = Field(..., max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., max_length=255, description="Email администратора")
    role: AdminRole = Field(..., description="Роль администратора")
    is_active: bool = Field(..., description="Активен ли администратор")
    created_at: str = Field(..., description="Дата создания")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "id": 1,
                "username": "admin",
                "email": "admin@example.com",
                "role": "admin",
                "is_active": True,
                "created_at": "2024-01-01T00:00:00Z",
            }
        }
    )


class AdminPasswordResetRequest(BaseModel):
    """Схема запроса восстановления пароля для POST /api/v1/admin/auth/password-reset."""

    email: EmailStr = Field(..., description="Email для восстановления пароля")

    model_config = ConfigDict(json_schema_extra={"example": {"email": "admin@example.com"}})


class AdminPasswordResetConfirmRequest(BaseModel):
    """Схема подтверждения восстановления пароля для POST /api/v1/admin/auth/password-reset-confirm."""

    token: str = Field(..., description="Токен восстановления из письма")
    new_password: str = Field(..., min_length=6, max_length=100, description="Новый пароль")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {"token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...", "new_password": "new_admin123"}
        }
    )


class AdminPasswordResetSuccessResponse(BaseModel):
    """Схема ответа успешного восстановления пароля."""

    message: str = Field(..., description="Сообщение об успешной смене")
    access_token: str = Field(..., description="Новый JWT токен доступа")
    refresh_token: str = Field(..., description="Refresh токен")
    token_type: str = Field(default="bearer", description="Тип токена")
    expires_in: int = Field(..., description="Время жизни токена в секундах")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "message": "Пароль успешно изменен",
                "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
                "token_type": "bearer",
                "expires_in": 3600,
            }
        }
    )
