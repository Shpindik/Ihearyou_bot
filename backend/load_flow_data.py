#!/usr/bin/env python3
"""Скрипт для загрузки данных в соответствии с flow и ссылками с сайта ihearyou.ru."""

import asyncio
import os
import sys
from typing import Any, Dict, List

from sqlalchemy import delete, select


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.db import AsyncSessionLocal
from backend.core.security import get_password_hash
from backend.crud import ContentFileCRUD, MenuItemCRUD
from backend.models.admin_user import AdminUser
from backend.models.content_file import ContentFile
from backend.models.enums import (
    AccessLevel,
    ActivityType,
    AdminRole,
    ContentType,
    ItemType,
    NotificationStatus,
    QuestionStatus,
    SubscriptionType,
)
from backend.models.menu_item import MenuItem
from backend.models.notification import Notification
from backend.models.question import UserQuestion
from backend.models.reminder_template import ReminderTemplate
from backend.models.telegram_user import TelegramUser
from backend.models.user_activity import UserActivity


class FlowDataLoader:
    """Класс для загрузки данных в соответствии с flow."""

    def __init__(self):
        """Инициализация загрузчика данных."""
        self.menu_item_crud = MenuItemCRUD()
        self.content_crud = ContentFileCRUD()

    async def clear_existing_data(self, session):
        """Очистить существующие данные."""
        print("🧹 Очистка существующих данных...")

        # Удаляем в правильном порядке из-за внешних ключей
        await session.execute(delete(UserActivity))
        await session.execute(delete(UserQuestion))
        await session.execute(delete(Notification))
        await session.execute(delete(TelegramUser))
        await session.execute(delete(AdminUser))
        await session.execute(delete(ReminderTemplate))
        await session.execute(delete(ContentFile))
        await session.execute(delete(MenuItem))

        await session.commit()
        print("✅ Данные очищены")

    async def create_main_menu_items(self, session):
        """Создать основные пункты меню - навигационные и контентные кнопки после /start."""
        print("📋 Создание основных пунктов меню...")

        main_items = [
            {
                "title": "Я волнуюсь о слухе ребенка",
                "description": "Информация и поддержка для родителей детей с нарушением слуха",
                "bot_message": "Понимание ваших беспокойств. Давайте разберем, что вас интересует:",
                "item_type": ItemType.NAVIGATION,
            },
            {
                "title": "Я волнуюсь о своем слухе",
                "description": "Информация и поддержка для взрослых с нарушением слуха",
                "bot_message": "Понимание ваших беспокойств. Давайте разберем, что vous интересует:",
                "item_type": ItemType.NAVIGATION,
            },
            {
                "title": "Проверить слух онлайн",
                "description": "Быстрая проверка слуха за 5 минут",
                "bot_message": "Проверьте свой слух прямо сейчас!",
                "item_type": ItemType.CONTENT,
                "content_type": ContentType.WEB_APP,
                "external_url": "https://www.ihearyou.ru/",
                "web_app_short_name": "hearing_test",
            },
            {
                "title": "Информация о нас",
                "description": "Кто мы и что делаем",
                "bot_message": "Узнайте больше о нашей организации:",
                "item_type": ItemType.CONTENT,
                "content_type": ContentType.EXTERNAL_URL,
                "external_url": "https://www.ihearyou.ru/",
            },
        ]

        for item_data in main_items:
            # Создаем новый пункт меню
            menu_item = MenuItem(
                title=item_data["title"],
                description=item_data["description"],
                bot_message=item_data["bot_message"],
                parent_id=None,
                item_type=item_data["item_type"],
                is_active=True,
                access_level=AccessLevel.FREE,
            )
            session.add(menu_item)
            await session.flush()  # Получаем ID

            # Создаем контент только для CONTENT типа
            if item_data["item_type"] == ItemType.CONTENT:
                content = ContentFile(
                    menu_item_id=menu_item.id,
                    content_type=item_data["content_type"],
                )

                # В зависимости от типа контента заполняем нужные поля
                if item_data["content_type"] == ContentType.WEB_APP:
                    content.web_app_short_name = item_data["web_app_short_name"]
                elif item_data["content_type"] == ContentType.EXTERNAL_URL:
                    content.external_url = item_data["external_url"]

                session.add(content)

        await session.commit()
        print("✅ Основные пункты меню созданы")

    async def create_child_subitems(self, session):
        """Создать подразделы для основных пунктов меню."""
        print("📋 Создание подразделов...")

        # Находим ID пункта "Я волнуюсь о слухе ребенка"
        child_item = await session.execute(
            select(MenuItem).where(MenuItem.title == "Я волнуюсь о слухе ребенка").limit(1)
        )
        child_item = child_item.first()
        if not child_item:
            print("❌ Пункт 'Я волнуюсь о слухе ребенка' не найден")
            return

        child_item = child_item[0]  # Получаем объект из кортежа

        child_subitems = [
            {
                "title": "Диагноз",
                "description": "Информация о диагностике слуха у детей",
                "bot_message": "Выберите раздел диагностики:",
                "item_type": ItemType.CONTENT,
                "content_type": ContentType.TEXT,
                "content": "🔍 **Диагностика слуха у детей**\n\nДля правильной диагностики слуха у детей необходимо:\n\n1. **Аудиометрия** - проверка остроты слуха\n2. **Тимпанометрия** - оценка состояния среднего уха\n3. **Речевая аудиометрия** - проверка разборчивости речи\n4. **Игровая аудиометрия** - для детей младшего возраста\n\nРекомендуется проходить диагностику у специалиста-сурдолога.\n\nПодробнее: https://www.ihearyou.ru/",
            },
            {
                "title": "Слуховые аппараты",
                "description": "Всё о слуховых аппаратах для детей",
                "bot_message": "Выберите раздел о слуховых аппаратах:",
                "item_type": ItemType.CONTENT,
                "content_type": ContentType.EXTERNAL_URL,
                "external_url": "https://www.ihearyou.ru/",
            },
            {
                "title": "Обучение и развитие",
                "description": "Материалы для обучения и развития детей",
                "bot_message": "Выберите раздел обучения:",
                "item_type": ItemType.NAVIGATION,
            },
            {
                "title": "Помощь специалиста",
                "description": "Получите консультацию эксперта через Web App",
                "bot_message": "Нужна помощь профессионала?",
                "item_type": ItemType.CONTENT,
                "content_type": ContentType.WEB_APP,
                "external_url": "https://www.ihearyou.ru/",
                "web_app_short_name": "specialist_consultation",
            },
        ]

        await self._create_subitems(session, child_item.id, child_subitems)
        print("✅ Подразделы для 'Я волнуюсь о слухе ребенка' созданы")

        # Создаем дочерние элементы для "Обучение и развитие"
        learning_item = await session.execute(
            select(MenuItem)
            .where(MenuItem.parent_id == child_item.id, MenuItem.title == "Обучение и развитие")
            .limit(1)
        )
        learning_item = learning_item.first()
        if learning_item:
            learning_item = learning_item[0]
            learning_subitems = [
                {
                    "title": "Раннее развитие (0-3 года)",
                    "description": "Материалы для раннего развития детей",
                    "bot_message": "Материалы для раннего развития:",
                    "item_type": ItemType.CONTENT,
                    "content_type": ContentType.TEXT,
                    "content": "🥺 **Раннее развитие ребенка (0-3 года)**\n\n**Основные принципы:**\n\n• Развитие слухового внимания с рождения\n• Использование звуков разной интенсивности\n• Игровые упражнения для стимуляции слуха\n• Постоянное ношение слуховых аппаратов\n\n**Важные моменты:**\n- Регулярные занятия с сурдологом\n- Музыкальные игрушки для развития\n- Пальчиковые игры с ритмом\n- Чтение вслух с четкой артикуляцией\n\nДетали: https://www.ihearyou.ru/",
                },
                {
                    "title": "Истории семей",
                    "description": "Вдохновляющие истории родителей",
                    "bot_message": "Прочитайте истории семей:",
                    "item_type": ItemType.CONTENT,
                    "content_type": ContentType.EXTERNAL_URL,
                    "external_url": "https://www.ihearyou.ru/",
                },
            ]
            await self._create_subitems(session, learning_item.id, learning_subitems)
            print("✅ Подразделы для 'Обучение и развитие' созданы")

        # Находим ID пункта "Я волнуюсь о своем слухе"
        adult_item = await session.execute(
            select(MenuItem).where(MenuItem.title == "Я волнуюсь о своем слухе").limit(1)
        )
        adult_item = adult_item.first()
        if not adult_item:
            print("❌ Пункт 'Я волнуюсь о своем слухе' не найден")
            return

        adult_item = adult_item[0]  # Получаем объект из кортежа

        adult_subitems = [
            {
                "title": "Проверка слуха",
                "description": "Как проверить свой слух",
                "bot_message": "Проверьте свой слух прямо сейчас:",
                "item_type": ItemType.CONTENT,
                "content_type": ContentType.TEXT,
                "content": "🔍 **Проверка слуха онлайн**\n\n**Онлайн-тест слуха:**\n\n• **Быстрая проверка** - 5 минут\n• **Точные результаты** - рекомендации специалиста\n• **Бесплатно** - для всех пользователей\n\n**Симптомы нарушения слуха:**\n• Трудности в понимании речи\n• Частые просьбы повторить\n• Увеличение громкости телевизора\n• Проблемы в шумной обстановке\n\n**Пройдите тест:** https://www.ihearyou.ru/\n\nПодробнее: https://www.ihearyou.ru/",
            },
            {
                "title": "Слуховые аппараты",
                "description": "Всё о слуховых аппаратах для взрослых",
                "bot_message": "Материалы о слуховых аппаратах:",
                "item_type": ItemType.CONTENT,
                "content_type": ContentType.EXTERNAL_URL,
                "external_url": "https://www.ihearyou.ru/",
            },
            {
                "title": "Сохранение слуха",
                "description": "Как сохранить и защитить слух",
                "bot_message": "Узнайте, как сохранить слух:",
                "item_type": ItemType.CONTENT,
                "content_type": ContentType.WEB_APP,
                "external_url": "https://www.ihearyou.ru/",
                "web_app_short_name": "hearing_care_tips",
            },
            {
                "title": "Помощь специалиста",
                "description": "Получите консультацию эксперта",
                "bot_message": "Нужна помощь профессионала?",
                "item_type": ItemType.NAVIGATION,
            },
        ]

        await self._create_subitems(session, adult_item.id, adult_subitems)
        print("✅ Подразделы для 'Я волнуюсь о своем слухе' созданы")

        # Создаем дочерние элементы для "Помощь специалиста"
        specialist_item = await session.execute(
            select(MenuItem).where(MenuItem.parent_id == adult_item.id, MenuItem.title == "Помощь специалиста").limit(1)
        )
        specialist_item = specialist_item.first()
        if specialist_item:
            specialist_item = specialist_item[0]
            specialist_subitems = [
                {
                    "title": "Консультация онлайн",
                    "description": "Получите консультацию специалиста в режиме онлайн",
                    "bot_message": "Записывайтесь на онлайн консультацию:",
                    "item_type": ItemType.CONTENT,
                    "content_type": ContentType.WEB_APP,
                    "external_url": "https://www.ihearyou.ru/",
                    "web_app_short_name": "online_consultation",
                },
                {
                    "title": "Контакты специалистов",
                    "description": "Специалисты готовы вам помочь",
                    "bot_message": "Наши контакты:",
                    "item_type": ItemType.CONTENT,
                    "content_type": ContentType.TEXT,
                    "content": "👨‍⚕️ **Контакты специалистов**\n\nНаши специалисты готовы помочь вам:\n\n**Телефоны для консультаций:**\n📞 +7 911 282 48 55\n📞 +7 921 930 78 63\n\n**Email:** info@ihearyou.ru\n\n**Адрес:**\nРоссия, г. Санкт-Петербург,\nул. Варшавская, 23-2-306\n\n**Режим работы:** Пн-Пт: 9:00-18:00\n\nПодробнее: https://www.ihearyou.ru/",
                },
            ]
            await self._create_subitems(session, specialist_item.id, specialist_subitems)
            print("✅ Подразделы для 'Помощь специалиста' созданы")

    async def _create_subitems(self, session, parent_id: int, subitems: List[Dict[str, Any]]):
        """Создать подразделы для родительского пункта меню."""
        for subitem_data in subitems:
            # Создаем пункт меню
            menu_item = MenuItem(
                title=subitem_data["title"],
                description=subitem_data["description"],
                bot_message=subitem_data["bot_message"],
                parent_id=parent_id,
                item_type=subitem_data["item_type"],
                is_active=True,
                access_level=AccessLevel.FREE,
            )
            session.add(menu_item)
            await session.flush()  # Получаем ID

            # Создаем контент только для CONTENT типа
            if subitem_data["item_type"] == ItemType.CONTENT:
                content = ContentFile(
                    menu_item_id=menu_item.id,
                    content_type=subitem_data["content_type"],
                )

                # В зависимости от типа контента заполняем нужные поля
                if subitem_data["content_type"] == ContentType.TEXT:
                    content.text_content = subitem_data.get("content")
                elif subitem_data["content_type"] == ContentType.WEB_APP:
                    content.external_url = subitem_data.get("external_url")
                    content.web_app_short_name = subitem_data.get("web_app_short_name")
                elif subitem_data["content_type"] == ContentType.EXTERNAL_URL:
                    content.external_url = subitem_data.get("external_url")

                session.add(content)

        await session.commit()

    async def create_admin_users(self, session):
        """Создать тестовых администраторов."""
        print("👨‍💼 Создание администраторов...")

        admin_users = [
            {
                "username": "admin",
                "email": "admin@ihearyou.ru",
                "password": "admin123",
                "role": AdminRole.ADMIN,
            },
            {
                "username": "moderator",
                "email": "moderator@ihearyou.ru",
                "password": "moderator123",
                "role": AdminRole.MODERATOR,
            },
        ]

        for user_data in admin_users:
            password_hash = get_password_hash(user_data["password"])
            admin = AdminUser(
                username=user_data["username"],
                email=user_data["email"],
                password_hash=password_hash,
                role=user_data["role"],
                is_active=True,
            )
            session.add(admin)

        await session.commit()
        print("✅ Администраторы созданы")

    async def create_telegram_users(self, session):
        """Создать тестовых пользователей Telegram."""
        print("👥 Создание пользователей Telegram...")

        telegram_users = [
            {
                "telegram_id": 123456789,
                "username": "parent_user",
                "first_name": "Анна",
                "last_name": "Петрова",
                "subscription_type": SubscriptionType.FREE,
            },
            {
                "telegram_id": 987654321,
                "username": "adult_user",
                "first_name": "Михаил",
                "last_name": "Иванов",
                "subscription_type": SubscriptionType.FREE,
            },
            {
                "telegram_id": 456789123,
                "username": "specialist_mom",
                "first_name": "Елена",
                "last_name": "Сидорова",
                "subscription_type": SubscriptionType.PREMIUM,
            },
        ]

        for user_data in telegram_users:
            telegram_user = TelegramUser(**user_data)
            session.add(telegram_user)

        await session.commit()
        print("✅ Пользователи Telegram созданы")

    async def create_reminder_templates(self, session):
        """Создать шаблоны напоминаний."""
        print("⏰ Создание шаблонов напоминаний...")

        templates = [
            {
                "name": "Еженедельное напоминание о проверке слуха",
                "message_template": "👋 Привет! 👉 Регулярная проверка слуха важна для здоровья. Пройдите тест: https://www.ihearyou.ru/\n\n📞 Консультация: +7 911 282 48 55",
            },
            {
                "name": "Напоминание о записи к специалисту",
                "message_template": "👨‍⚕️ Не забывайте о плановых осмотрах! Запишитесь на консультацию к специалисту.\n\n📞 +7 911 282 48 55\n📧 info@ihearyou.ru",
            },
            {
                "name": "Полезные советы по сохранению слуха",
                "message_template": "🛡️ Советы для сохранения слуха:\n• Избегайте громких звуков\n• Ограничьте время в наушниках\n• Регулярно проверяйте слух\n\nПодробнее: https://www.ihearyou.ru/",
            },
        ]

        for template_data in templates:
            template = ReminderTemplate(**template_data)
            session.add(template)

        await session.commit()
        print("✅ Шаблоны напоминаний созданы")

    async def create_user_questions_and_activities(self, session):
        """Создать тестовые вопросы и активности пользователей."""
        print("❓ Создание вопросов и активностей...")

        # Получаем пользователей для создания вопросов
        tg_users_result = await session.execute(select(TelegramUser))
        tg_users = tg_users_result.scalars().all()

        # Получаем пункты меню для активностей
        menu_items_result = await session.execute(select(MenuItem))
        menu_items = menu_items_result.scalars().all()

        # Получаем администратора для ответов
        admin_result = await session.execute(select(AdminUser).limit(1))
        admin = admin_result.scalar()

        if tg_users and menu_items:
            # Создаем вопросы
            questions = [
                {
                    "telegram_user_id": tg_users[0].id,
                    "question_text": "Ребенку 2 года, плохо реагирует на звуки. Как понять, нужна ли ему помощь специалиста?",
                    "status": QuestionStatus.ANSWERED,
                    "answer_text": "В 2 года важно своевременно диагностировать проблемы слуха. Рекомендую обратиться к детскому сурдологу для комплексного обследования. Запишитесь: +7 911 282 48 55",
                    "admin_user_id": admin.id if admin else None,
                },
                {
                    "telegram_user_id": tg_users[1].id,
                    "question_text": "Стоит ли покупать слуховой аппарат самостоятельно или обязательно консультироваться с врачом?",
                    "status": QuestionStatus.PENDING,
                    "answer_text": None,
                    "admin_user_id": None,
                },
                {
                    "telegram_user_id": tg_users[2].id,
                    "question_text": "Как часто нужно проверять слух ребенку со слуховыми аппаратами?",
                    "status": QuestionStatus.ANSWERED,
                    "answer_text": "Рекомендуется проверка слуха каждые 3-6 месяцев для детей со слуховыми аппаратами.",
                    "admin_user_id": admin.id if admin else None,
                },
            ]

            for question_data in questions:
                question = UserQuestion(**question_data)
                session.add(question)

            # Создаем активности пользователей
            activities = [
                {
                    "telegram_user_id": tg_users[0].id,
                    "activity_type": ActivityType.START_COMMAND,
                    "menu_item_id": None,
                },
                {
                    "telegram_user_id": tg_users[0].id,
                    "activity_type": ActivityType.NAVIGATION,
                    "menu_item_id": menu_items[0].id if menu_items else None,
                },
                {
                    "telegram_user_id": tg_users[0].id,
                    "activity_type": ActivityType.TEXT_VIEW,
                    "menu_item_id": menu_items[0].id if menu_items else None,
                },
                {
                    "telegram_user_id": tg_users[1].id,
                    "activity_type": ActivityType.START_COMMAND,
                    "menu_item_id": None,
                },
                {
                    "telegram_user_id": tg_users[1].id,
                    "activity_type": ActivityType.MATERIAL_OPEN,
                    "menu_item_id": menu_items[1].id if len(menu_items) > 1 else None,
                },
                {
                    "telegram_user_id": tg_users[2].id,
                    "activity_type": ActivityType.SEARCH,
                    "search_query": "слуховые аппараты для детей",
                },
                {
                    "telegram_user_id": tg_users[2].id,
                    "activity_type": ActivityType.RATING,
                    "menu_item_id": menu_items[1].id if len(menu_items) > 1 else None,
                    "rating": 5,
                },
            ]

            for activity_data in activities:
                activity = UserActivity(**activity_data)
                session.add(activity)

        await session.commit()
        print("✅ Вопросы и активности созданы")

    async def create_notifications(self, session):
        """Создать тестовые уведомления."""
        print("📬 Создание уведомлений...")

        # Получаем пользователей и шаблоны
        tg_users_result = await session.execute(select(TelegramUser))
        tg_users = tg_users_result.scalars().all()

        templates_result = await session.execute(select(ReminderTemplate))
        templates = templates_result.scalars().all()

        notifications = [
            {
                "telegram_user_id": tg_users[0].id,
                "message": "Добро пожаловать в наш бот! 🎉 Мы поможем вам с вопросами слуха",
                "status": NotificationStatus.SENT,
                "template_id": None,
            },
            {
                "telegram_user_id": tg_users[1].id,
                "message": templates[0].message_template,
                "status": NotificationStatus.PENDING,
                "template_id": templates[0].id if templates else None,
            },
            {
                "telegram_user_id": tg_users[2].id,
                "message": "Ваш вопрос получил ответ от специалиста! 👨‍⚕️",
                "status": NotificationStatus.SENT,
                "template_id": None,
            },
        ]

        for notification_data in notifications:
            notification = Notification(**notification_data)
            session.add(notification)

        await session.commit()
        print("✅ Уведомления созданы")

    async def load_all_data(self):
        """Загрузить все данные."""
        async with AsyncSessionLocal() as session:
            try:
                await self.clear_existing_data(session)

                # Создаём основные данные системы
                await self.create_reminder_templates(session)
                await self.create_admin_users(session)
                await self.create_main_menu_items(session)
                await self.create_child_subitems(session)
                await self.create_telegram_users(session)
                await self.create_user_questions_and_activities(session)
                await self.create_notifications(session)

                print("\n🎉 Все данные успешно загружены!")
                print("\n📊 Статистика:")
                print("• Администраторов: 2 (admin + moderator)")
                print("• Пользователей Telegram: 3")
                print("• Шаблонов напоминаний: 3")
                print("• Основных разделов меню: 4")
                print("  - Навигационные: 2")
                print("  - Контентные (TEXT/EXTERNAL_URL/WEB_APP): 2")
                print("• Подразделов первого уровня: 8")
                print("  - Навигационные: 2")
                print("  - Контентные с текстом: 2")
                print("  - Контентные с внешними ссылками: 2")
                print("  - Контентные с Web App: 2")
                print("• Подразделов второго уровня: 4")
                print("  - Контентные с текстом: 2")
                print("  - Контентные с внешними ссылками: 1")
                print("  - Контентные с Web App: 1")
                print("• Всего пунктов меню: 16 (4 основных + 12 подразделов)")
                print("• Контентных блоков: 14")
                print("• Вопросов пользователей: 3 (2 ответленных + 1 в ожидании)")
                print("• Активностей пользователей: 7")
                print("• Уведомлений: 3 (2 отправленных + 1 в ожидании)")

            except Exception as e:
                print(f"❌ Ошибка при загрузке данных: {e}")
                await session.rollback()
                raise


async def main():
    """Основная функция."""
    print("🚀 Запуск загрузки данных в соответствии с flow...")

    loader = FlowDataLoader()
    await loader.load_all_data()

    print("\n✅ Загрузка завершена успешно!")


if __name__ == "__main__":
    asyncio.run(main())
