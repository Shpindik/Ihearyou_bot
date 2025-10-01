from fastapi import Request
from fastapi.responses import JSONResponse

from backend.core.exceptions import ValidationError


def register_exception_handlers(app):
    @app.exception_handler(ValidationError)
    async def validation_exception_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=422,
            content={"detail": str(exc)},
        )
