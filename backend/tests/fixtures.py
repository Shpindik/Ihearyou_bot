"""Фикстуры данных для тестов."""

import datetime
from datetime import timezone

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.admin_user import AdminUser
from backend.models.enums import AccessLevel, AdminRole, ItemType
from backend.models.menu_item import MenuItem
from backend.models.message_template import MessageTemplate
from backend.models.telegram_user import TelegramUser


@pytest_asyncio.fixture
async def admin_user(db_session: AsyncSession):
    """Создать администратора.

    Пароль: 'testpassword123'
    """
    # Это хеш пароля 'testpassword123'
    # Сгенерирован заранее для тестов
    user = AdminUser(
        username="testadmin",
        email="testadmin@example.com",
        password_hash="$pbkdf2-sha256$29000$yplz7p2T8v6/915rzXlPSQ$TkT.RrmE6JMKt4QpuzCq9Ah8ewTejLK0LtmnwRVbehA",
        is_active=True,
        role=AdminRole.ADMIN
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def moderator_user(db_session: AsyncSession):
    """Создать модератора.

    Пароль: 'testpassword123'
    """
    user = AdminUser(
        username="testmoderator",
        email="testmoderator@example.com",
        password_hash="$pbkdf2-sha256$29000$yplz7p2T8v6/915rzXlPSQ$TkT.RrmE6JMKt4QpuzCq9Ah8ewTejLK0LtmnwRVbehA",
        is_active=True,
        role=AdminRole.MODERATOR
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def user_free(db_session: AsyncSession):
    """Создать бесплатного пользователя."""
    user = TelegramUser(
        telegram_id=123456789,
        username="freeuser",
        first_name="Free",
        last_name=None,
        subscription_type=AccessLevel.FREE,
        created_at=datetime.datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user.telegram_id


@pytest_asyncio.fixture
async def user_premium(db_session: AsyncSession):
    """Создать премиум пользователя."""
    user = TelegramUser(
        telegram_id=987654321,
        username="premiumuser",
        first_name="Premium",
        last_name=None,
        subscription_type=AccessLevel.PREMIUM,
        created_at=datetime.datetime.now(timezone.utc),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user.telegram_id




@pytest_asyncio.fixture
async def telegram_users_fixture(db_session: AsyncSession):
    """Создать тестовых пользователей Telegram."""
    users = [
        TelegramUser(
            telegram_id=111111111,
            username="testuser1",
            first_name="Test",
            last_name="User1",
            subscription_type=AccessLevel.FREE,
            created_at=datetime.datetime.now(timezone.utc),
            activities_count=5,
            questions_count=3,
        ),
        TelegramUser(
            telegram_id=222222222,
            username="testuser2",
            first_name="Another",
            last_name="User2",
            subscription_type=AccessLevel.PREMIUM,
            created_at=datetime.datetime.now(timezone.utc),
            activities_count=10,
            questions_count=7,
        ),
        TelegramUser(
            telegram_id=333333333,
            username=None,
            first_name="NoUsername",
            last_name=None,
            subscription_type=AccessLevel.FREE,
            created_at=datetime.datetime.now(timezone.utc),
            activities_count=1,
            questions_count=0,
        ),
    ]
    db_session.add_all(users)
    await db_session.commit()
    for user in users:
        await db_session.refresh(user)
        db_session.expunge(user)
    return users


@pytest_asyncio.fixture
async def menu_items_fixture(db_session: AsyncSession):
    """Создать тестовые пункты меню."""
    items = [
        # Корневые пункты меню
        MenuItem(
            title="Root Free Item",
            description="Free navigation item",
            item_type=ItemType.NAVIGATION,
            is_active=True,
            access_level=AccessLevel.FREE,
            bot_message="Free navigation menu",
            created_at=datetime.datetime.now(timezone.utc),
        ),
        MenuItem(
            title="Root Premium Item",
            description="Premium navigation item",
            item_type=ItemType.NAVIGATION,
            is_active=True,
            access_level=AccessLevel.PREMIUM,
            bot_message="Premium navigation menu",
            created_at=datetime.datetime.now(timezone.utc),
        ),
        MenuItem(
            title="Inactive Root Item",
            description="Inactive navigation item",
            item_type=ItemType.NAVIGATION,
            is_active=False,
            access_level=AccessLevel.FREE,
            bot_message="Inactive menu",
            created_at=datetime.datetime.now(timezone.utc),
        ),
        # Дочерние пункты
        MenuItem(
            title="Free Content Item",
            description="Free content item",
            parent_id=None,  # Будет установлено после создания
            item_type=ItemType.CONTENT,
            is_active=True,
            access_level=AccessLevel.FREE,
            bot_message="This is free content",
            created_at=datetime.datetime.now(timezone.utc),
        ),
        MenuItem(
            title="Premium Content Item",
            description="Premium content item",
            parent_id=None,  # Будет установлено после создания
            item_type=ItemType.CONTENT,
            is_active=True,
            access_level=AccessLevel.PREMIUM,
            bot_message="This is premium content",
            created_at=datetime.datetime.now(timezone.utc),
        ),
    ]
    db_session.add_all(items)
    await db_session.commit()

    # Обновляем parent_id для дочерних элементов
    for item in items:
        await db_session.refresh(item)

    # Устанавливаем parent_id для дочерних элементов
    free_content = next(item for item in items if item.title == "Free Content Item")
    premium_content = next(item for item in items if item.title == "Premium Content Item")
    free_root = next(item for item in items if item.title == "Root Free Item")
    premium_root = next(item for item in items if item.title == "Root Premium Item")

    free_content.parent_id = free_root.id
    premium_content.parent_id = premium_root.id

    await db_session.commit()

    for item in items:
        await db_session.refresh(item)
        db_session.expunge(item)

    return items


@pytest_asyncio.fixture
async def active_template(db_session: AsyncSession):
    """Создать активный шаблон сообщения."""
    template = MessageTemplate(
        name="Active template",
        message_template="Hello, {first_name}! Message for active template",
        is_active=True,
        created_at=datetime.datetime(2024, 10, 10, tzinfo=timezone.utc),
        updated_at=datetime.datetime(2024, 10, 10, tzinfo=timezone.utc),
    )
    db_session.add(template)
    await db_session.commit()
    await db_session.refresh(template)
    db_session.expunge(template)
    return template


@pytest_asyncio.fixture
async def inactive_template(db_session: AsyncSession):
    """Создать неактивный шаблон сообщения."""
    template = MessageTemplate(
        name="Inactive template",
        message_template="Message for inactive template",
        is_active=False,
        created_at=datetime.datetime(2024, 10, 10, tzinfo=timezone.utc),
        updated_at=datetime.datetime(2024, 10, 10, tzinfo=timezone.utc),
    )
    db_session.add(template)
    await db_session.commit()
    await db_session.refresh(template)
    db_session.expunge(template)
    return template


@pytest.fixture
def admin_user_crud():
    """Фикстура для AdminUserCRUD."""
    from backend.crud.admin_user import AdminUserCRUD
    return AdminUserCRUD()


@pytest.fixture
def menu_item_crud():
    """Фикстура для MenuItemCRUD."""
    from backend.crud.menu_item import MenuItemCRUD
    return MenuItemCRUD()


@pytest.fixture
def telegram_user_crud():
    """Фикстура для TelegramUserCRUD."""
    from backend.crud.telegram_user import TelegramUserCRUD
    return TelegramUserCRUD()


@pytest.fixture
def user_activity_crud():
    """Фикстура для UserActivityCRUD."""
    from backend.crud.user_activity import UserActivityCRUD
    return UserActivityCRUD()


# Фикстуры сервисов и утилит
@pytest.fixture
def analytics_crud():
    """Фикстура AnalyticsCRUD."""
    from backend.crud.analytics import AnalyticsCRUD
    return AnalyticsCRUD()


@pytest.fixture
def analytics_validator():
    """Фикстура AnalyticsValidator."""
    from backend.validators.analytics import AnalyticsValidator
    return AnalyticsValidator()


@pytest.fixture
def analytics_service():
    """Фикстура AnalyticsService."""
    from backend.services.analytics import AnalyticsService
    return AnalyticsService()


@pytest.fixture
def admin_user_service():
    """Фикстура AdminUserService."""
    from backend.services.admin_user import AdminUserService
    return AdminUserService()


@pytest.fixture
def admin_user_validator():
    """Фикстура AdminUserValidator."""
    from backend.validators.admin_user import AdminUserValidator
    return AdminUserValidator()


@pytest.fixture
def email_service(mocker, monkeypatch):
    """Фикстура EmailService с моками."""
    from backend.utils.email import EmailService

    # Мокаем FastMail и settings
    mock_settings = mocker.MagicMock()
    mock_settings.frontend_url = "http://test.com"
    mock_settings.email_conf.return_value = mocker.MagicMock()

    mock_fastmail = mocker.AsyncMock()

    monkeypatch.setattr("backend.utils.email.settings", mock_settings)
    monkeypatch.setattr("backend.utils.email.FastMail", mocker.MagicMock(return_value=mock_fastmail))

    service = EmailService()
    service.fastmail = mock_fastmail
    return service

