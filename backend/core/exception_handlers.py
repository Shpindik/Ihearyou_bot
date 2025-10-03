"""Глобальные обработчики исключений для FastAPI."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from backend.core.exceptions import (
    AuthenticationError,
    AuthorizationError,
    ConflictError,
    IHearYouException,
    MediaValidationError,
    NotFoundError,
    ValidationError,
)


if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрация глобальных обработчиков исключений.

    Args:
        app: Экземпляр FastAPI приложения
    """

    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError) -> JSONResponse:
        """Обработчик ошибок валидации."""
        logger.warning(f"Validation error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"error": {"code": "validation_error", "message": exc.message, "details": exc.details}},
        )

    @app.exception_handler(AuthenticationError)
    async def authentication_exception_handler(request: Request, exc: AuthenticationError) -> JSONResponse:
        """Обработчик ошибок аутентификации."""
        logger.warning(f"Authentication error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": {"code": "authentication_error", "message": exc.message, "details": exc.details}},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(AuthorizationError)
    async def authorization_exception_handler(request: Request, exc: AuthorizationError) -> JSONResponse:
        """Обработчик ошибок авторизации."""
        logger.warning(f"Authorization error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": {"code": "authorization_error", "message": exc.message, "details": exc.details}},
        )

    @app.exception_handler(NotFoundError)
    async def not_found_exception_handler(request: Request, exc: NotFoundError) -> JSONResponse:
        """Обработчик ошибок - ресурс не найден."""
        logger.info(f"Resource not found: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"error": {"code": "not_found", "message": exc.message, "details": exc.details}},
        )

    @app.exception_handler(ConflictError)
    async def conflict_exception_handler(request: Request, exc: ConflictError) -> JSONResponse:
        """Обработчик ошибок конфликта данных."""
        logger.warning(f"Conflict error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"error": {"code": "conflict_error", "message": exc.message, "details": exc.details}},
        )

    @app.exception_handler(MediaValidationError)
    async def media_validation_exception_handler(request: Request, exc: MediaValidationError) -> JSONResponse:
        """Обработчик ошибок валидации медиафайлов."""
        logger.warning(f"Media validation error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"error": {"code": "media_validation_error", "message": exc.message, "details": exc.details}},
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Обработчик ошибок базы данных."""
        logger.error(f"Database error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "database_error",
                    "message": "Ошибка базы данных",
                    "details": {"type": type(exc).__name__},
                }
            },
        )

    @app.exception_handler(IHearYouException)
    async def ihearyou_exception_handler(request: Request, exc: IHearYouException) -> JSONResponse:
        """Обработчик базовых исключений приложения."""
        logger.error(f"Application error: {exc.message}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"error": {"code": "application_error", "message": exc.message, "details": exc.details}},
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Обработчик общих исключений."""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "internal_server_error",
                    "message": "Внутренняя ошибка сервера",
                    "details": {"type": type(exc).__name__},
                }
            },
        )
