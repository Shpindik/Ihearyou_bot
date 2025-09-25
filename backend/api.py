from __future__ import annotations

import os

import aiohttp
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import authenticate_user, create_access_token, get_current_active_admin
from .database import get_session
from .models import AdminUser, User
from .schemas import AdminUserResponse, Token, UserResponse

router = APIRouter(prefix="/api")


@router.post("/auth/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
):
    user = await authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Неверный логин или пароль")
    token = create_access_token({"sub": user.username})
    return Token(access_token=token)


@router.get("/auth/me", response_model=AdminUserResponse)
async def read_current_user(current_user: AdminUser = Depends(get_current_active_admin)):
    return current_user


@router.get("/users/{user_id}/avatar")
async def get_user_avatar(user_id: int):
    token = os.getenv("BOT_TOKEN")
    if not token:
        return Response(status_code=204)

    api_base = f"https://api.telegram.org/bot{token}"
    try:
        async with aiohttp.ClientSession() as http:
            # Получаем фото профиля (только одно последнее)
            async with http.get(f"{api_base}/getUserProfilePhotos", params={"user_id": user_id, "limit": 1}) as r1:
                if r1.status != 200:
                    return Response(status_code=204)
                data1 = await r1.json()
            if not data1.get("ok") or data1.get("result", {}).get("total_count", 0) == 0:
                return Response(status_code=204)

            photos = data1["result"]["photos"][0]
            largest = photos[-1]
            file_id = largest["file_id"]

            async with http.get(f"{api_base}/getFile", params={"file_id": file_id}) as r2:
                if r2.status != 200:
                    return Response(status_code=204)
                data2 = await r2.json()
            if not data2.get("ok"):
                return Response(status_code=204)

            file_path = data2["result"]["file_path"]
            file_url = f"https://api.telegram.org/file/bot{token}/{file_path}"

            async with http.get(file_url) as r3:
                if r3.status != 200:
                    return Response(status_code=204)
                content = await r3.read()
                content_type = r3.headers.get("Content-Type", "image/jpeg")
                resp = Response(content=content, media_type=content_type)
                resp.headers["Cache-Control"] = "public, max-age=86400"
                return resp
    except Exception:
        return Response(status_code=204)


@router.get("/users", response_model=list[UserResponse])
async def list_users(
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: AdminUser = Depends(get_current_active_admin),
):
    del current_user
    stmt = (
        select(
            User.id,
            User.user_id,
            User.username,
            User.fullname,
        )
        .order_by(User.id.desc())
        .limit(200)
    )
    rows = (await session.execute(stmt)).all()
    base_url = str(request.base_url)

    def to_item(row):
        id_, uid, username, fullname = row
        avatar_url = f"{base_url}api/users/{uid or 0}/avatar" if uid is not None else None
        return UserResponse(
            id=id_,
            user_id=uid,
            username=username,
            fullname=fullname,
            avatar_url=avatar_url,
        )

    return [to_item(r) for r in rows]
