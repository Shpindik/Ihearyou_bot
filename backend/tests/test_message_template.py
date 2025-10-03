import pytest


ADMIN_REMINDERS_URL = "/api/v1/admin/message-templates/"
ADMIN_REMINDERS_DETAIL_URL = ADMIN_REMINDERS_URL + "{template_id}"
ADMIN_REMINDERS_DETAIL_ACTIVATE_URL = ADMIN_REMINDERS_DETAIL_URL + "/activate"
ADMIN_REMINDERS_DETAIL_DEACTIVATE_URL = ADMIN_REMINDERS_DETAIL_URL + "/deactivate"
BOT_GET_TEMPLATE = "/api/v1/bot/message-template/active-template"


@pytest.mark.asyncio
async def test_admin_get_all_templates(admin_client, inactive_template, active_template):
    response = await admin_client.get(ADMIN_REMINDERS_URL)
    assert response.status_code == 200, (
        f"GET-запрос админа к эндпоинту `{ADMIN_REMINDERS_URL}` должен вернуть ответ со статус-кодом 200."
    )
    response_data = response.json()
    assert "items" in response_data
    items = response_data.get("items")
    assert isinstance(items, list)
    assert len(items) == 2, (
        "Ответ на GET-запрос админа к эндпоинту "
        f"`{ADMIN_REMINDERS_URL}` должен содержать данные всех шаблонов."
    )
    first_elem = items[0]
    expected_keys = {"id", "name", "message_template", "is_active", "created_at", "updated_at"}
    missing_keys = expected_keys - first_elem.keys()
    assert not missing_keys, (
        'В ответе на GET-запрос админа к эндпоинту '
        f'`{ADMIN_REMINDERS_URL}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )
    assert sorted(items, key=lambda x: x["id"]) == sorted(
        [
            {   
                "id": inactive_template.id,
                "name": inactive_template.name,
                "message_template": inactive_template.message_template,
                "is_active": inactive_template.is_active,
                "created_at": "2024-10-10T00:00:00",
                "updated_at": "2024-10-10T00:00:00",
            },
            {
                "id": active_template.id,
                "name": active_template.name,
                "message_template": active_template.message_template,
                "is_active": active_template.is_active,
                "created_at": "2024-10-10T00:00:00",
                "updated_at": "2024-10-10T00:00:00",
            },
        ],
        key=lambda x: x["id"],
    ), (
        "При запросе на получение списка всех шаблонов тело ответа API отличается от ожидаемого."
    )


@pytest.mark.asyncio
@pytest.mark.parametrize("json_data, expected_data", [
    (
        {
            "message_template": "Привет! У нас есть новые материалы, которые могут быть полезны для вас.",
            "name": "Active template"
        },
        {       
            "id": 1,
            "message_template": "Привет! У нас есть новые материалы, которые могут быть полезны для вас.",
            "name": "Active template",
            "is_active": True
        }
    ),
    (
        {
            "message_template": "Привет! У нас есть новые материалы, которые могут быть полезны для вас",
            "name": "Inactive template",
            "is_active": False
        },
        {       
            "id": 1,
            "name": "Inactive template",
            "message_template": "Привет! У нас есть новые материалы, которые могут быть полезны для вас",
            "is_active": False,
        }
    )
])
async def test_admin_create_templates(admin_client, json_data, expected_data):
    response = await admin_client.post(ADMIN_REMINDERS_URL, json=json_data)
    assert response.status_code == 201, (
        f"POST-запрос админа к эндпоинту `{ADMIN_REMINDERS_URL}` должен вернуть ответ со статус-кодом 201."
    )
    data = response.json()
    expected_keys = {"id", "name", "message_template", "is_active", "created_at", "updated_at"}
    missing_keys = expected_keys - data.keys()
    assert not missing_keys, (
        'В ответе на POST-запрос админа к эндпоинту '
        f'`{ADMIN_REMINDERS_URL}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )
    data.pop("created_at")
    data.pop("updated_at")
    assert data == expected_data


@pytest.mark.asyncio
@pytest.mark.parametrize("json_data", [
    {"name": "", "message_template": "empty name" * 10},
    {"name": 10, "message_template": "integer name" * 10},
    {"name": "ab", "message_template": "short name" * 10},
    {"name": None, "message_template": "Null name" * 10},
    {"name": "integer message", "message_template": 10},
    {"name": "null massage", "message_template": None},
    {"name": "too_long" * 32, "message_template": "too long name " * 10},
    {"name": "too_long_message", "message_template": "a" * 4001},
    {"name": "Wrong is_active", "message_template": "We miss you" * 10, "is_active": "active"},
    {"name": "Wrong is_active", "message_template": "We miss you" * 10, "is_active": None},
    {"name": "Wrong is_active", "message_template": "We miss you" * 10, "is_active": 2},
])
async def test_create_template_incorrect(admin_client, json_data):
    response = await admin_client.post(ADMIN_REMINDERS_URL, json=json_data)
    assert response.status_code == 422, (
        f"При некорректном теле POST-запроса к эндпоинту `{ADMIN_REMINDERS_URL}` "
        "должен вернуться статус-код 422."
    )


@pytest.mark.asyncio
async def test_unautherised_user_cant_create_template(async_client, active_template):
    response = await async_client.put(
        ADMIN_REMINDERS_DETAIL_URL.format(template_id=active_template.id),
        json={"name": "test_name", "message_template": "We miss you"}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.parametrize("json_data, expected_data", [
    (
        {},
        {       
            "id": 1,
            "name": "Active template",
            "message_template": "Message for active template",
            "is_active": True,
            "created_at": "2024-10-10T00:00:00",
        }
    ),
    (
        {"name": "Other_name", "message_template": "Other_message template message", "is_active": False},
        {       
            "id": 1,
            "name": "Other_name",
            "message_template": "Other_message template message",
            "is_active": False,
            "created_at": "2024-10-10T00:00:00",
        }
    )
])
async def test_admin_update_template(admin_client, json_data, expected_data, active_template):
    response = await admin_client.put(ADMIN_REMINDERS_DETAIL_URL.format(template_id=active_template.id), json=json_data)
    assert response.status_code == 200, (
        f"PUT-запрос админа к эндпоинту `{ADMIN_REMINDERS_DETAIL_URL}` должен вернуть ответ со статус-кодом 200."
    )
    data = response.json()
    expected_keys = {"id", "name", "message_template", "is_active", "created_at", "updated_at"}
    missing_keys = expected_keys - data.keys()
    assert not missing_keys, (
        'В ответе на PUT-запрос админа к эндпоинту '
        f'`{ADMIN_REMINDERS_DETAIL_URL}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )
    data.pop("updated_at")
    assert data == expected_data


@pytest.mark.asyncio
async def test_unautherised_user_cant_update_template(async_client, active_template):
    response = await async_client.put(
        ADMIN_REMINDERS_DETAIL_URL.format(template_id=active_template.id),
        json={"name": "Other_name", "message_template": "Other_message", "is_active": False}
    )
    assert response.status_code == 403


@pytest.mark.asyncio
@pytest.mark.parametrize("json_data", [
    {"name": ""},
    {"name": 100},
    {"name": "aa"},
    {"message_template": ""},
    {"message_template": 5},
    {"message_template": "a" * 19},
    {"message_template": "a" * 4001},
    {"name": "too_long" * 32},
    {"is_active": "active"},
    {"is_active": 2},
])
async def test_update_template_incorrect(admin_client, json_data, active_template):
    response = await admin_client.put(ADMIN_REMINDERS_DETAIL_URL.format(template_id=active_template.id), json=json_data)
    assert response.status_code == 422, (
        f"При некорректном теле PUT-запроса к эндпоинту `{ADMIN_REMINDERS_DETAIL_URL}` "
        "должен вернуться статус-код 422."
    )


@pytest.mark.asyncio
async def test_admin_delete_template(admin_client, active_template):
    response = await admin_client.get(ADMIN_REMINDERS_URL)
    objects_before = len(response.json().get("items"))
    response = await admin_client.delete(ADMIN_REMINDERS_DETAIL_URL.format(template_id=active_template.id))
    assert response.status_code == 204, (
        f"DELETE-запрос админа к эндпоинту `{ADMIN_REMINDERS_DETAIL_URL}` должен вернуть ответ со статус-кодом 200."
    )
    response = await admin_client.get(ADMIN_REMINDERS_URL)
    objects_after = len(response.json().get("items"))
    assert objects_after == objects_before - 1, (
        f"DELETE-запрос админа к эндпоинту `{ADMIN_REMINDERS_DETAIL_URL}` должен удалять объект."
    )


@pytest.mark.asyncio
async def test_unautherised_user_cant_delete_template(async_client, active_template):
    response = await async_client.delete(ADMIN_REMINDERS_DETAIL_URL.format(template_id=active_template.id))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_admin_activate_template(admin_client, inactive_template):
    response = await admin_client.post(ADMIN_REMINDERS_DETAIL_ACTIVATE_URL.format(template_id=inactive_template.id))
    assert response.status_code == 200
    data = response.json()
    expected_keys = {"id", "name", "message_template", "is_active", "created_at", "updated_at"}
    missing_keys = expected_keys - data.keys()
    assert not missing_keys, (
        'В ответе на POST-запрос админа к эндпоинту '
        f'`{ADMIN_REMINDERS_DETAIL_ACTIVATE_URL}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )
    assert data.get("is_active")
    expected_data = {
        "id": inactive_template.id,
        "name": inactive_template.name,
        "message_template": inactive_template.message_template,
        "is_active": True,
        "created_at": "2024-10-10T00:00:00"
    }
    data.pop("updated_at")
    assert data == expected_data


@pytest.mark.asyncio
async def test_admin_deactivate_template(admin_client, active_template):
    response = await admin_client.post(ADMIN_REMINDERS_DETAIL_DEACTIVATE_URL.format(template_id=active_template.id))
    assert response.status_code == 200
    data = response.json()
    expected_keys = {"id", "name", "message_template", "is_active", "created_at", "updated_at"}
    missing_keys = expected_keys - data.keys()
    assert not missing_keys, (
        'В ответе на POST-запрос админа к эндпоинту '
        f'`{ADMIN_REMINDERS_DETAIL_DEACTIVATE_URL}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )
    assert not data.get("is_active")
    expected_data = {
        "id": active_template.id,
        "name": active_template.name,
        "message_template": active_template.message_template,
        "is_active": False,
        "created_at": "2024-10-10T00:00:00"
    }
    data.pop("updated_at")
    assert data == expected_data


@pytest.mark.asyncio
async def test_unautherised_user_cant_activate_template(async_client, inactive_template):
    response = await async_client.post(ADMIN_REMINDERS_DETAIL_ACTIVATE_URL.format(template_id=inactive_template.id))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_unautherised_user_cant_deactivate_template(async_client, active_template):
    response = await async_client.post(ADMIN_REMINDERS_DETAIL_DEACTIVATE_URL.format(template_id=active_template.id))
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_bot_get_active_template(async_client, active_template):
    response = await async_client.get(BOT_GET_TEMPLATE)
    assert response.status_code == 200, (
        f"GET-запрос админа к эндпоинту `{BOT_GET_TEMPLATE}` должен вернуть ответ со статус-кодом 200."
    )
    response_data = response.json()
    expected_keys = {"id", "name", "message_template", "created_at"}
    missing_keys = expected_keys - response_data.keys()
    assert not missing_keys, (
        'В ответе на GET-запрос админа к эндпоинту '
        f'`{BOT_GET_TEMPLATE}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )


@pytest.mark.asyncio
async def test_bot_get_template_while_no_templates(async_client):
    response = await async_client.get(BOT_GET_TEMPLATE)
    assert response.status_code == 200, (
        f"GET-запрос админа к эндпоинту `{BOT_GET_TEMPLATE}` должен вернуть ответ со статус-кодом 200."
    )
    response_data = response.json()
    expected_keys = {"id", "name", "message_template", "created_at"}
    missing_keys = expected_keys - response_data.keys()
    assert not missing_keys, (
        'В ответе на GET-запрос админа к эндпоинту '
        f'`{BOT_GET_TEMPLATE}` не хватает следующих ключей: '
        f'`{"`, `".join(missing_keys)}`'
    )