"""Административные схемы для управления администраторами."""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from backend.models.enums import AdminRole


class AdminUserResponse(BaseModel):
    """Схема данных администратора для GET /api/v1/admin/users/{id}."""

    id: int = Field(..., description="ID администратора")
    username: str = Field(..., max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., max_length=255, description="Email администратора")
    role: AdminRole = Field(..., description="Роль администратора")
    is_active: bool = Field(..., description="Активен ли администратор")
    created_at: datetime = Field(..., description="Дата создания")

    model_config = ConfigDict(from_attributes=True)


class AdminUserListResponse(BaseModel):
    """Схема ответа списка администраторов для GET /api/v1/admin/users."""

    items: List[AdminUserResponse] = Field(..., description="Список администраторов")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "items": [
                    {
                        "id": 1,
                        "username": "admin",
                        "email": "admin@example.com",
                        "role": "admin",
                        "is_active": True,
                        "created_at": "2024-01-01T00:00:00Z",
                    }
                ]
            }
        }
    )


class AdminUserCreate(BaseModel):
    """Схема запроса создания администратора для POST /api/v1/admin/users."""

    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email администратора")
    password: str = Field(..., min_length=6, max_length=100, description="Пароль")
    role: AdminRole = Field(default=AdminRole.MODERATOR, description="Роль администратора")
    is_active: bool = Field(default=True, description="Активен ли администратор")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "new_admin",
                "email": "new.admin@example.com",
                "password": "admin123",
                "role": "moderator",
                "is_active": True,
            }
        }
    )


class AdminUserUpdate(BaseModel):
    """Схема запроса обновления администратора для PUT /api/v1/admin/users/{id}."""

    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Имя пользователя")
    email: Optional[EmailStr] = Field(None, description="Email администратора")
    role: Optional[AdminRole] = Field(None, description="Роль администратора")
    is_active: Optional[bool] = Field(None, description="Активен ли администратор")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "username": "updated_admin",
                "email": "updated.admin@example.com",
                "role": "admin",
                "is_active": False,
            }
        }
    )


class AdminUserPasswordUpdate(BaseModel):
    """Схема запроса смены пароля администратора для PUT /api/v1/admin/users/{id}/password."""

    new_password: str = Field(..., min_length=6, max_length=100, description="Новый пароль")

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "new_password": "new_admin123",
            }
        }
    )
