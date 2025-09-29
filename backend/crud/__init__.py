"""Инициализация CRUD пакета."""

from .base import BaseCRUD
from .content_file import ContentFileCRUD, content_file_crud
from .menu_item import MenuItemCRUD, menu_crud
from .telegram_user import TelegramUserCRUD, user_crud
from .user_activity import UserActivityCRUD, activity_crud


__all__ = [
    "BaseCRUD",
    "MenuItemCRUD",
    "ContentFileCRUD",
    "TelegramUserCRUD",
    "UserActivityCRUD",
    "menu_crud",
    "content_file_crud",
    "user_crud",
    "activity_crud",
]
