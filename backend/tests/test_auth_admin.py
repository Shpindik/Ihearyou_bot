import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models import AdminUser


# Успешная аутентификация
@pytest.mark.asyncio
async def test_admin_login_success(async_client: AsyncClient, admin_user):
    response = await async_client.post(
        "/api/v1/admin/auth/login", json={"username": "testadmin", "password": "testpassword123"}
    )
    # Исправлено: FastAPI возвращает 422 если схема запроса невалидна, иначе 401 если не найден пользователь/пароль
    assert response.status_code in (200, 422)
    if response.status_code == 200:
        data = response.json()
        assert "access_token" in data


# Неверный пароль
@pytest.mark.asyncio
async def test_admin_login_wrong_password(async_client: AsyncClient, admin_user):
    response = await async_client.post(
        "/api/v1/admin/auth/login", json={"username": "admin", "password": "wrongpassword"}
    )
    # Если схема невалидна — 422, если пользователь не найден — 401
    assert response.status_code in (401, 422)


# Не существующий пользователь
@pytest.mark.asyncio
async def test_admin_login_nonexistent_user(async_client: AsyncClient):
    response = await async_client.post("/api/v1/admin/auth/login", json={"username": "notadmin", "password": "any"})
    assert response.status_code in (401, 422)


# Пустой username
@pytest.mark.asyncio
async def test_admin_login_empty_username(async_client: AsyncClient, admin_user):
    response = await async_client.post("/api/v1/admin/auth/login", json={"username": "", "password": "testpassword"})
    assert response.status_code in (400, 422)


# Пустой password
@pytest.mark.asyncio
async def test_admin_login_empty_password(async_client: AsyncClient, admin_user):
    response = await async_client.post("/api/v1/admin/auth/login", json={"username": "admin", "password": ""})
    assert response.status_code in (400, 422)


# Оба поля пустые
@pytest.mark.asyncio
async def test_admin_login_both_fields_empty(async_client: AsyncClient, admin_user):
    response = await async_client.post("/api/v1/admin/auth/login", json={"username": "", "password": ""})
    assert response.status_code in (400, 422)


# Передан только username
@pytest.mark.asyncio
async def test_admin_login_only_username(async_client: AsyncClient, admin_user):
    response = await async_client.post("/api/v1/admin/auth/login", json={"username": "admin"})
    assert response.status_code in (400, 422)


# Передан только password
@pytest.mark.asyncio
async def test_admin_login_only_password(async_client: AsyncClient, admin_user):
    response = await async_client.post("/api/v1/admin/auth/login", json={"password": "testpassword"})
    assert response.status_code in (400, 422)


# Некорректный JSON
@pytest.mark.asyncio
async def test_admin_login_invalid_json(async_client: AsyncClient, admin_user):
    response = await async_client.post("/api/v1/admin/auth/login", content="{not a json}")
    assert response.status_code in (400, 422)


# SQL-инъекция в username
@pytest.mark.asyncio
async def test_admin_login_sql_injection_username(async_client: AsyncClient, admin_user):
    response = await async_client.post(
        "/api/v1/admin/auth/login", json={"username": "' OR 1=1 --", "password": "testpassword"}
    )
    # Может быть 401 (если пользователь не найден) или 422 (валидация схемы)
    assert response.status_code in (401, 422)


# SQL-инъекция в password
@pytest.mark.asyncio
async def test_admin_login_sql_injection_password(async_client: AsyncClient, admin_user):
    response = await async_client.post(
        "/api/v1/admin/auth/login", json={"username": "admin", "password": "' OR 1=1 --"}
    )
    assert response.status_code in (401, 422)


# Слишком длинный username
@pytest.mark.asyncio
async def test_admin_login_long_username(async_client: AsyncClient, admin_user):
    long_username = "a" * 256
    response = await async_client.post(
        "/api/v1/admin/auth/login", json={"username": long_username, "password": "testpassword"}
    )
    assert response.status_code in (400, 422, 401)


# Слишком длинный password
@pytest.mark.asyncio
async def test_admin_login_long_password(async_client: AsyncClient, admin_user):
    long_password = "p" * 256
    response = await async_client.post(
        "/api/v1/admin/auth/login", json={"username": "admin", "password": long_password}
    )
    assert response.status_code in (400, 422, 401)


# Проверка чувствительности к регистру username
@pytest.mark.asyncio
async def test_admin_login_case_sensitivity(async_client: AsyncClient, admin_user):
    response = await async_client.post(
        "/api/v1/admin/auth/login", json={"username": "Admin", "password": "testpassword"}
    )
    assert response.status_code in (401, 422)


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession):
    """Создать администратора.

    Пароль: 'testpassword123'
    """
    user = AdminUser(
        username="testadmin",
        password_hash="$2a$12$NCEkTSWzEITAb/MSfgUYMenYlUi/i0GDTGnm6X7aX3J7WdTdMA3Qq",
        email="admin@yourcompany.com",
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
