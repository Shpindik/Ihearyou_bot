from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select

from .api import router as api_router
from .auth import pwd_context
from .database import AsyncSessionLocal
from .models import AdminUser

app = FastAPI(title="PhotoBot Admin API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.on_event("startup")
async def ensure_default_admin() -> None:
    username = os.getenv("ADMIN_USERNAME", "admin")
    password = os.getenv("ADMIN_PASSWORD", "admin12345")
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(AdminUser).where(AdminUser.username == username))
        user = result.scalar_one_or_none()
        password_hash = pwd_context.hash(password)
        if user is None:
            session.add(AdminUser(username=username, password_hash=password_hash, role="admin", is_active=True))
        else:
            user.password_hash = password_hash
            user.is_active = True
            user.role = user.role or "admin"
        await session.commit()
