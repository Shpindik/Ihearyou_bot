import pytest


ADMIN_NOTIFICTIONS_URL = "/api/v1/admin/notifications/"
ADMIN_NOTIFICTIONS_DETAIL_URL = ADMIN_NOTIFICTIONS_URL + "{id}"
ADMIN_NOTIFICTIONS_STATISTIC_URL = ADMIN_NOTIFICTIONS_URL + "statistics"


@pytest.mark.asyncio
async def test_admin_create_notification(admin_client, inactive_telegram_user, freezer):
    freezer.move_to("2025-01-25")
    json_data = {
        "message": "Напоминание: не забудьте проверить новые материалы!",
        "telegram_user_id": 123456789
    }
    response = await admin_client.post(ADMIN_NOTIFICTIONS_URL, json=json_data)
    assert response.status_code == 201, (
        f"POST-запрос админа к эндпоинту `{ADMIN_NOTIFICTIONS_URL}` должен вернуть ответ со статус-кодом 201."
    )
    data = response.json()
    expected_keys = {"id", "telegram_user_id", "message", "status", "created_at", "sent_at", "template_id"}
    missing_keys = expected_keys - data.keys()
    assert not missing_keys, (
        'В ответе на POST-запрос админа к эндпоинту '
        f'`{ADMIN_NOTIFICTIONS_URL}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )
    expected_data = {
        "id": 1,
        "telegram_user_id": 123456789,
        "message": "Напоминание: не забудьте проверить новые материалы!",
        "status": "pending",
        "created_at": "2025-01-25T00:00:00",
        "sent_at": None,
        "template_id": None
    }
    assert data == expected_data


@pytest.mark.asyncio
@pytest.mark.parametrize("json_data, expected_code", [
    ({"message": "Тест! Пользователь не найден", "telegram_user_id": 111111111}, 404),
    ({"message": "Too short", "telegram_user_id": 123456789}, 422),
])
async def test_admin_create_notification_incorrect(admin_client, json_data, expected_code, inactive_telegram_user):
    response = await admin_client.post(ADMIN_NOTIFICTIONS_URL, json=json_data)
    assert response.status_code == expected_code


@pytest.mark.asyncio
async def test_admin_update_sent_notification(admin_client, pending_notification, freezer):
    freezer.move_to("2025-01-25")
    json_data = {"sent_at": "2025-01-25T20:00:00Z", "status": "sent"}
    assert pending_notification.id == 1
    response = await admin_client.put(ADMIN_NOTIFICTIONS_DETAIL_URL.format(id=pending_notification.id), json=json_data)
    assert response.status_code == 200, (
        f"PUT-запрос админа к эндпоинту `{ADMIN_NOTIFICTIONS_DETAIL_URL}` должен вернуть ответ со статус-кодом 200."
    )
    data = response.json()
    expected_keys = {"id", "telegram_user_id", "message", "status", "created_at", "sent_at", "template_id"}
    missing_keys = expected_keys - data.keys()
    assert not missing_keys, (
        'В ответе на POST-запрос админа к эндпоинту '
        f'`{ADMIN_NOTIFICTIONS_DETAIL_URL}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )
    expected_data = {
        "id": 1,
        "telegram_user_id": 123456789,
        "message": "Ожидающее напоминание: не забудьте проверить новые материалы!",
        "status": "sent",
        "created_at": "2025-01-15T00:00:00",
        "sent_at": "2025-01-25T00:00:00Z",
        "template_id": None
    }
    assert data == expected_data


@pytest.mark.asyncio
async def test_admin_update_failed_notification(admin_client, pending_notification, freezer):
    freezer.move_to("2025-01-25")
    json_data = {"sent_at": "2025-01-25T20:00:00Z", "status": "failed"}
    assert pending_notification.id == 1
    response = await admin_client.put(ADMIN_NOTIFICTIONS_DETAIL_URL.format(id=pending_notification.id), json=json_data)
    assert response.status_code == 200, (
        f"PUT-запрос админа к эндпоинту `{ADMIN_NOTIFICTIONS_DETAIL_URL}` должен вернуть ответ со статус-кодом 200."
    )
    data = response.json()
    expected_data = {
        "id": 1,
        "telegram_user_id": 123456789,
        "message": "Ожидающее напоминание: не забудьте проверить новые материалы!",
        "status": "failed",
        "created_at": "2025-01-15T00:00:00",
        "sent_at": None,
        "template_id": None
    }
    assert data == expected_data


@pytest.mark.asyncio
async def test_admin_get_notifications(admin_client, sent_notification, failed_notification, pending_notification, freezer):
    freezer.move_to("2025-01-25")
    response = await admin_client.get(ADMIN_NOTIFICTIONS_URL, params={"days_ago": 30})
    assert response.status_code == 200, (
        f"GET-запрос админа к эндпоинту `{ADMIN_NOTIFICTIONS_URL}` должен вернуть ответ со статус-кодом 200."
    )
    data = response.json()
    expected_keys = {"items", "total", "page", "limit", "pages"}
    missing_keys = expected_keys - data.keys()
    assert not missing_keys, (
        'В ответе на POST-запрос админа к эндпоинту '
        f'`{ADMIN_NOTIFICTIONS_URL}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )
    items = data.get("items")
    assert isinstance(items, list)
    assert len(items) == 3


@pytest.mark.asyncio
async def test_admin_get_notification_statistics(admin_client, sent_notification, failed_notification, pending_notification):
    response = await admin_client.get(ADMIN_NOTIFICTIONS_STATISTIC_URL)
    assert response.status_code == 200, (
        f"GET-запрос админа к эндпоинту `{ADMIN_NOTIFICTIONS_STATISTIC_URL}` должен вернуть ответ со статус-кодом 200."
    )
    data = response.json()
    expected_keys = {"total", "sent", "failed", "pending", "success_rate"}
    missing_keys = expected_keys - data.keys()
    assert not missing_keys, (
        'В ответе на GET-запрос админа к эндпоинту '
        f'`{ADMIN_NOTIFICTIONS_STATISTIC_URL}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )
    expected_data = {
        "total": 3,
        "sent": 1,
        "failed": 1,
        "pending": 1,
        "success_rate": 33.33
    }
    assert data == expected_data