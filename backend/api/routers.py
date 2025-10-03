"""Централизованное подключение всех роутеров API."""

from fastapi import APIRouter

from .v1 import api_v1_router


# Создание главного роутера API
api_router = APIRouter()

# Подключение главного роутера API v1
api_router.include_router(api_v1_router)
