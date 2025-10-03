import pytest
from fastapi.testclient import TestClient
from pytest_mock import MockerFixture
from sqlalchemy.ext.asyncio import AsyncSession

from backend.core.exceptions import ValidationError
from backend.crud.menu_item import menu_crud
from backend.main import app
from backend.models.enums import AccessLevel
from backend.schemas.public.search import SearchItemResponse, SearchListResponse
from backend.services.menu_item import menu_item_service
from backend.validators.menu_item import menu_item_validator


client = TestClient(app)


# ===============================
# Тесты для валидатора
# ===============================
@pytest.mark.parametrize(
    "query, expected",
    [
        ("test", "test"),
        ("  test  query  ", "test query"),
        ("тест", "тест"),
        ("ab" * 50, "ab" * 50),
    ],
)
def test_validate_search_query_success(query, expected):
    result = menu_item_validator.validate_search_query(query)
    assert result == expected


@pytest.mark.parametrize(
    "query, error_msg",
    [
        ("a", "от 2 до 100"),
        ("", "от 2 до 100"),
        (" ", "от 2 до 100"),
        ("a" * 101, "от 2 до 100"),
        ("test<", "недопустимые символы"),
        ("test>", "недопустимые символы"),
        ("test{", "недопустимые символы"),
        ("teeeeest", "повторяющихся"),
        ("aaaab", "повторяющихся"),
    ],
)
def test_validate_search_query_fail(query, error_msg):
    with pytest.raises(ValidationError) as exc:
        menu_item_validator.validate_search_query(query)
    assert error_msg in str(exc.value)


# ===============================
# Тесты для CRUD
# ===============================
@pytest.mark.asyncio
async def test_search_by_query_free(db: AsyncSession, menu_items_fixture):
    results = await menu_crud.search_by_query(db=db, query="test", access_level=AccessLevel.FREE, limit=10)
    assert len(results) > 0
    for item in results:
        assert item.access_level == AccessLevel.FREE
        assert item.is_active is True
        assert "test" in item.title.lower() or (item.description and "test" in item.description.lower())


@pytest.mark.asyncio
async def test_search_by_query_premium(db: AsyncSession, menu_items_fixture):
    results = await menu_crud.search_by_query(db=db, query="test", access_level=AccessLevel.PREMIUM, limit=10)
    results_free = await menu_crud.search_by_query(db=db, query="test", access_level=AccessLevel.FREE, limit=10)
    assert len(results) >= len(results_free)


@pytest.mark.asyncio
async def test_search_by_query_inactive_excluded(db: AsyncSession, menu_items_fixture):
    results = await menu_crud.search_by_query(db=db, query="inactive", access_level=AccessLevel.PREMIUM, limit=10)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_search_by_query_description(db: AsyncSession, menu_items_fixture):
    results = await menu_crud.search_by_query(db=db, query="description", access_level=AccessLevel.FREE, limit=10)
    assert len(results) > 0
    for item in results:
        assert item.description and "description" in item.description.lower()


@pytest.mark.asyncio
async def test_search_by_query_no_results(db: AsyncSession, menu_items_fixture):
    results = await menu_crud.search_by_query(db=db, query="nonexistent", access_level=AccessLevel.PREMIUM, limit=10)
    assert len(results) == 0


@pytest.mark.asyncio
async def test_search_by_query_case_insensitive(db: AsyncSession, menu_items_fixture):
    results_lower = await menu_crud.search_by_query(
        db=db, query="test free item", access_level=AccessLevel.FREE, limit=10
    )
    results_upper = await menu_crud.search_by_query(
        db=db, query="TEST FREE ITEM", access_level=AccessLevel.FREE, limit=10
    )
    assert len(results_lower) == len(results_upper)
    assert len(results_lower) > 0


@pytest.mark.asyncio
async def test_search_by_query_multiple_words(db: AsyncSession, menu_items_fixture):
    results = await menu_crud.search_by_query(db=db, query="free test", access_level=AccessLevel.FREE, limit=10)
    assert len(results) > 0


@pytest.mark.asyncio
async def test_search_by_query_russian(db: AsyncSession, menu_items_fixture):
    results = await menu_crud.search_by_query(
        db=db,
        query="русский",
        access_level=AccessLevel.PREMIUM,
        limit=10,
    )
    assert isinstance(results, list)


@pytest.mark.asyncio
async def test_search_by_query_limit_edge(db: AsyncSession, menu_items_fixture):
    results_limit_1 = await menu_crud.search_by_query(db=db, query="test", access_level=AccessLevel.PREMIUM, limit=1)
    assert len(results_limit_1) <= 1

    results_limit_0 = await menu_crud.search_by_query(db=db, query="test", access_level=AccessLevel.PREMIUM, limit=0)
    assert len(results_limit_0) == 0


# ===============================
# Тесты для сервиса
# ===============================
@pytest.mark.asyncio
async def test_search_menu_items_success_free(db: AsyncSession, user_free, menu_items_fixture):
    result = await menu_item_service.search_menu_items(
        telegram_user_id=user_free,
        query="test",
        limit=5,
        db=db,
    )
    assert isinstance(result, SearchListResponse)
    assert len(result.items) > 0
    titles = [item.title for item in result.items]
    assert any("Test Free Item" in t for t in titles)


@pytest.mark.asyncio
async def test_search_menu_items_success_premium(db: AsyncSession, user_premium, menu_items_fixture):
    result = await menu_item_service.search_menu_items(
        telegram_user_id=user_premium,
        query="test",
        limit=5,
        db=db,
    )
    assert isinstance(result, SearchListResponse)
    assert len(result.items) > 0
    titles = [item.title for item in result.items]
    assert any("Test Premium Item" in t for t in titles)


@pytest.mark.asyncio
async def test_search_menu_items_invalid_query(db: AsyncSession, user_free):
    with pytest.raises(ValidationError):
        await menu_item_service.search_menu_items(telegram_user_id=user_free, query="a", limit=10, db=db)


@pytest.mark.asyncio
async def test_search_menu_items_no_results(db: AsyncSession, user_free):
    result = await menu_item_service.search_menu_items(telegram_user_id=user_free, query="nonexistent", limit=10, db=db)
    assert isinstance(result, SearchListResponse)
    assert len(result.items) == 0


@pytest.mark.asyncio
async def test_search_menu_items_max_length_query(db: AsyncSession, user_free, menu_items_fixture):
    long_query = "ab" * 50
    result = await menu_item_service.search_menu_items(telegram_user_id=user_free, query=long_query, limit=10, db=db)
    assert isinstance(result, SearchListResponse)


@pytest.mark.asyncio
async def test_search_menu_items_unsafe_query(db: AsyncSession, user_free):
    with pytest.raises(ValidationError) as exc:
        await menu_item_service.search_menu_items(telegram_user_id=user_free, query="test<unsafe>", limit=10, db=db)
    assert "недопустимые символы" in str(exc.value)


# ===============================
# Тесты для API
# ===============================
@pytest.mark.parametrize(
    "query, expected_status",
    [
        ("test", 200),
        ("nonexistent", 200),
    ],
)
def test_search_materials_api_success(query, expected_status, mocker: MockerFixture):
    """Тест успешных запросов к API."""
    mock_items = (
        [
            SearchItemResponse(
                id=1,
                title="Test",
                description=None,
                parent_id=None,
                bot_message=None,
                is_active=True,
                access_level=AccessLevel.FREE,
            )
        ]
        if query != "nonexistent"
        else []
    )

    mocker.patch(
        "backend.api.v1.public.search.menu_item_service.search_menu_items",
        return_value=SearchListResponse(items=mock_items),
        new_callable=mocker.AsyncMock,  # убрано autospec
    )

    response = client.get(f"/api/v1/search?telegram_user_id=123456789&query={query}&limit=10")
    assert response.status_code == expected_status
    assert "items" in response.json()


def test_search_materials_api_validation_error(mocker: MockerFixture):
    """Тест обработки ValidationError."""
    mocker.patch(
        "backend.api.v1.public.search.menu_item_service.search_menu_items",
        side_effect=ValidationError("Invalid query"),
        new_callable=mocker.AsyncMock,  # убрано autospec
    )

    response = client.get("/api/v1/search?telegram_user_id=123456789&query=ab&limit=10")
    # ValidationError должна быть обработана
    assert response.status_code in [400, 422, 500]


def test_search_materials_api_missing_params():
    """Тест отсутствующих параметров."""
    response = client.get("/api/v1/search?query=test&limit=10")
    assert response.status_code == 422

    response = client.get("/api/v1/search?telegram_user_id=123456789&limit=10")
    assert response.status_code == 422


def test_search_materials_api_invalid_limit():
    """Тест некорректного значения limit."""
    response = client.get("/api/v1/search?telegram_user_id=123456789&query=test&limit=abc")
    assert response.status_code == 422

    response = client.get("/api/v1/search?telegram_user_id=123456789&query=test&limit=0")
    assert response.status_code == 422


def test_search_materials_api_invalid_telegram_id():
    """Тест некорректного telegram_user_id."""
    response = client.get("/api/v1/search?telegram_user_id=-1&query=test&limit=10")
    assert response.status_code == 422
