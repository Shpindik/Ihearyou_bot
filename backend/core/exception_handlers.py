"""Глобальные обработчики исключений для FastAPI."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from fastapi import HTTPException, Request, status
from fastapi.responses import JSONResponse
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import SQLAlchemyError


if TYPE_CHECKING:
    from fastapi import FastAPI

logger = logging.getLogger(__name__)


def register_exception_handlers(app: FastAPI) -> None:
    """Регистрация глобальных обработчиков исключений.

    Args:
        app: Экземпляр FastAPI приложения
    """

    @app.exception_handler(PydanticValidationError)
    async def pydantic_validation_exception_handler(request: Request, exc: PydanticValidationError) -> JSONResponse:
        """Обработчик ошибок валидации Pydantic."""
        logger.warning(f"Pydantic validation error: {exc}")
        errors = []
        for error in exc.errors():
            errors.append({"loc": list(error["loc"]), "msg": str(error["msg"]), "type": error["type"]})
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "detail": errors,
                "error": {"code": "VALIDATION_ERROR", "message": "Ошибка валидации данных", "details": errors},
            },
        )

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
        """Обработчик HTTP исключений из FastAPI и валидаторов."""
        logger.warning(f"HTTP exception: {exc.detail}")

        # Определяем код ошибки на основе статуса
        error_code = "HTTP_ERROR"
        if exc.status_code == 404:
            error_code = "NOT_FOUND"
        elif exc.status_code == 400:
            error_code = "VALIDATION_ERROR"
        elif exc.status_code == 401:
            error_code = "AUTHENTICATION_ERROR"
        elif exc.status_code == 403:
            error_code = "AUTHORIZATION_ERROR"
        elif exc.status_code == 409:
            error_code = "CONFLICT_ERROR"
        elif exc.status_code == 429:
            error_code = "RATE_LIMIT_EXCEEDED"

        return JSONResponse(
            status_code=exc.status_code,
            content={"detail": exc.detail, "error": {"code": error_code, "message": exc.detail}},
            headers=getattr(exc, "headers", None),
        )

    @app.exception_handler(SQLAlchemyError)
    async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        """Обработчик ошибок базы данных."""
        logger.error(f"Database error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "DATABASE_ERROR",
                    "message": "Ошибка базы данных",
                    "details": {"type": type(exc).__name__},
                }
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
        """Обработчик общих исключений."""
        logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_SERVER_ERROR",
                    "message": "Внутренняя ошибка сервера",
                    "details": {"type": type(exc).__name__},
                }
            },
        )
