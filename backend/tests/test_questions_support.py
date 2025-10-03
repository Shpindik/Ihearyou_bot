import pytest

from backend.services.question import user_question_service


@pytest.mark.asyncio
async def test_user_can_send_question(async_client, user_free):
    """Пользователь может отправить вопрос через API."""
    response = await async_client.post(
        "/api/v1/public/user-questions/",
        json={"telegram_user_id": user_free, "question_text": "Как пользоваться ботом?"},
    )
    assert response.status_code in (201, 200)
    data = response.json()
    assert data["question_text"] == "Как пользоваться ботом?"
    assert data["status"] == "pending"


@pytest.mark.asyncio
async def test_admin_can_list_questions(admin_client):
    """Админ может получить список вопросов."""
    response = await admin_client.get("/api/v1/admin/user-questions/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert isinstance(data.get("items"), list)


# Валидация
@pytest.mark.asyncio
async def test_question_empty_text(async_client, user_free):
    """Вопрос без текста не принимается."""
    response = await async_client.post(
        "/api/v1/public/user-questions/", json={"telegram_user_id": user_free, "question_text": ""}
    )
    assert response.status_code in (400, 422)


@pytest.mark.asyncio
async def test_question_too_short(async_client, user_free):
    response = await async_client.post(
        "/api/v1/public/user-questions/",
        json={"telegram_user_id": user_free, "question_text": "кa"},
    )
    assert response.status_code == 400
    assert "Текст вопроса должен содержать минимум 10 символов" in response.text


@pytest.mark.asyncio
async def test_question_too_long(async_client, user_free):
    long_text = "a" * 2001
    response = await async_client.post(
        "/api/v1/public/user-questions/",
        json={"telegram_user_id": user_free, "question_text": long_text},
    )
    assert response.status_code in (400, 422)
    if response.status_code == 400:
        assert "не может превышать 2000 символов" in response.text


@pytest.mark.asyncio
async def test_question_forbidden_chars(async_client, user_free):
    response = await async_client.post(
        "/api/v1/public/user-questions/",
        json={"telegram_user_id": user_free, "question_text": "Вопрос с <скобками>"},
    )
    assert response.status_code == 400
    assert "недопустимые символы" in response.text


@pytest.mark.asyncio
async def test_question_from_unknown_user(async_client):
    response = await async_client.post(
        "/api/v1/public/user-questions/",
        json={"telegram_user_id": 999999999, "question_text": "Вопрос от неизвестного"},
    )
    assert response.status_code == 400
    assert "Пользователь не найден" in response.text


@pytest.mark.asyncio
async def test_questions_statistics(async_client, db):

    stats = await user_question_service.get_questions_statistics(db)
    assert "total" in stats
    assert "pending" in stats
    assert "answered" in stats
