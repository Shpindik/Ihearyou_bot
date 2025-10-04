import pytest


BOT_GET_INACTIVE_USERS = "/api/v1/bot/telegram-user/inactive-users"
BOT_REGISTER_TELEGRAM_USER = "/api/v1/bot/telegram-user/register"
BOT_UPDATE_REMINDER_STATUS = "/api/v1/bot/telegram-user/update-reminder-status"


@pytest.mark.asyncio
async def test_bot_get_inactive_users(async_client, inactive_telegram_user, active_telegram_user, freezer):
    freezer.move_to("2025-01-17")
    response = await async_client.get(BOT_GET_INACTIVE_USERS)
    assert response.status_code == 200, (
        f"GET-запрос админа к эндпоинту `{BOT_GET_INACTIVE_USERS}` должен вернуть ответ со статус-кодом 200."
    )
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 1
    first_elem = response_data[0]
    expected_keys = {"first_name", "last_activity", "last_name", "telegram_user_id", "username"}
    missing_keys = expected_keys - first_elem.keys()
    assert not missing_keys, (
        'В ответе на GET-запрос админа к эндпоинту '
        f'`{BOT_GET_INACTIVE_USERS}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("params", [
    ({"inactive_days": 0}),
    ({"inactive_days": True}),
    ({"days_since_last_reminder": 0}),
    ({"days_since_last_reminder": False}),
])
async def test_bot_get_inactive_users_incorrect(async_client, params):
    response = await async_client.get(BOT_GET_INACTIVE_USERS, params=params)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_bot_get_all_inactive_users(async_client, inactive_telegram_user, active_telegram_user, freezer):
    freezer.move_to("2025-01-17")
    response = await async_client.get(BOT_GET_INACTIVE_USERS, params={"inactive_days": 1, "days_since_last_reminder": 1})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 2


@pytest.mark.asyncio
async def test_bot_get_only_inactive_users(async_client, inactive_telegram_user, active_telegram_user, freezer):
    freezer.move_to("2025-01-17")
    response = await async_client.get(BOT_GET_INACTIVE_USERS, params={"inactive_days": 100, "days_since_last_reminder": 100})
    assert response.status_code == 200
    response_data = response.json()
    assert len(response_data) == 0


@pytest.mark.asyncio
async def test_bot_create_telegram_user(async_client, freezer):
    freezer.move_to("2025-01-01")
    json_data = {
        "message": {
            "from": {
                "first_name": "Иван",
                "id": 123456789,
                "last_name": "Иванов",
                "username": "ivan_ivanov"
            }
        },
        "update_id": 123456789
    }
    response = await async_client.post(BOT_REGISTER_TELEGRAM_USER, json=json_data)
    assert response.status_code == 200
    data = response.json()
    expected_keys = {"user", "message_processed", "user_created", "user_updated"}
    missing_keys = expected_keys - data.keys()
    assert not missing_keys, (
        'В ответе на POST-запрос админа к эндпоинту '
        f'`{BOT_REGISTER_TELEGRAM_USER}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )
    assert data.get("message_processed")
    assert data.get("user_created")
    assert not data.get("user_updated")
    user = data.get("user")
    expected_user_data = {
        "id": 1,
        "first_name": "Иван",
        "telegram_id": 123456789,
        "last_name": "Иванов",
        "username": "ivan_ivanov",
        "subscription_type": "free",
        "last_activity": "2025-01-01T00:00:00",
        "reminder_sent_at": None,
        "created_at": "2025-01-01T00:00:00"
    }
    assert user == expected_user_data


@pytest.mark.asyncio
async def test_bot_update_telegram_user(async_client, inactive_telegram_user, freezer):
    freezer.move_to("2025-01-20")
    json_data = {
        "message": {
            "from": {
                "first_name": "Петр",
                "id": 123456789,
                "last_name": "Петров",
                "username": "ivan_ivanov"
            }
        },
        "update_id": 1234
    }
    response = await async_client.post(BOT_REGISTER_TELEGRAM_USER, json=json_data)
    assert response.status_code == 200
    data = response.json()
    assert data.get("message_processed")
    assert not data.get("user_created")
    assert data.get("user_updated")
    user = data.get("user")
    expected_user_data = {
        "id": 1,
        "first_name": "Петр",
        "telegram_id": 123456789,
        "last_name": "Петров",
        "username": "ivan_ivanov",
        "subscription_type": "free",
        "last_activity": "2025-01-20T00:00:00",
        "reminder_sent_at": "2025-01-01T00:00:00",
        "created_at": "2025-01-01T00:00:00"
    }
    assert user == expected_user_data


@pytest.mark.asyncio
async def test_bot_apdate_reminder_status(async_client, inactive_telegram_user, freezer):
    freezer.move_to("2025-01-25")
    params = {"telegram_user_id": 123456789}
    response = await async_client.post(BOT_UPDATE_REMINDER_STATUS, params=params)
    assert response.status_code == 200
    data = response.json()
    expected_keys = {  "message", "reminder_sent_at", "success"}
    missing_keys = expected_keys - data.keys()
    assert not missing_keys, (
        'В ответе на POST-запрос админа к эндпоинту '
        f'`{BOT_UPDATE_REMINDER_STATUS}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )
    assert data.get("reminder_sent_at") == "2025-01-25T00:00:00+00:00"


@pytest.mark.asyncio
@pytest.mark.parametrize("params, status_code", [
    ({"telegram_user_id": 111111111}, 400),
    ({"telegram_user_id": None}, 422),
])
async def test_bot_apdate_reminder_status_incorrect(async_client, params, status_code, inactive_telegram_user):
    response = await async_client.post(BOT_UPDATE_REMINDER_STATUS, params=params)
    assert response.status_code == status_code