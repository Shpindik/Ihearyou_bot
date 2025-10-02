"""HTTP клиент для взаимодействия с API бэкенда."""

import os
from typing import Dict, List, Optional

import aiohttp


class APIClient:
    """Клиент для работы с API бэкенда."""

    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "http://bot_api:8000/api/v1")
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Асинхронный контекстный менеджер - вход."""
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Асинхронный контекстный менеджер - выход."""
        if self.session:
            await self.session.close()

    async def get_menu_items(self, telegram_user_id: int, parent_id: Optional[int] = None) -> List[Dict]:
        """Получить пункты меню."""
        url = f"{self.base_url}/menu-items"
        params = {"telegram_user_id": telegram_user_id}
        if parent_id is not None:
            params["parent_id"] = parent_id

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("items", [])
                else:
                    print(f"Ошибка получения меню: {response.status}")
                    return []
        except Exception as e:
            print(f"Ошибка подключения к API: {e}")
            return []

    async def get_menu_content(
        self,
        menu_item_id: int,
        telegram_user_id: int
    ) -> Optional[Dict]:
        """Получить контент пункта меню."""
        url = f"{self.base_url}/menu-items/{menu_item_id}/content"
        params = {"telegram_user_id": telegram_user_id}

        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Ошибка получения контента: {response.status}")
                    return None
        except Exception as e:
            print(f"Ошибка подключения к API: {e}")
            return None

    async def record_activity(
        self,
        telegram_user_id: int,
        menu_item_id: int,
        activity_type: str,
        search_query: Optional[str] = None
    ) -> bool:
        """Записать активность пользователя."""
        url = f"{self.base_url}/user-activities"
        data = {
            "telegram_user_id": telegram_user_id,
            "menu_item_id": menu_item_id,
            "activity_type": activity_type
        }
        if search_query:
            data["search_query"] = search_query

        try:
            async with self.session.post(url, json=data) as response:
                return response.status == 201
        except Exception as e:
            print(f"Ошибка записи активности: {e}")
            return False

    async def rate_material(
        self,
        telegram_user_id: int,
        menu_item_id: int,
        rating: int
    ) -> bool:
        """Оценить материал через публичный API."""
        url = f"{self.base_url}/ratings"
        data = {
            "telegram_user_id": telegram_user_id,
            "menu_item_id": menu_item_id,
            "rating": rating,
        }
        try:
            async with self.session.post(url, json=data) as response:
                return response.status == 201
        except Exception as e:
            print(f"Ошибка отправки оценки: {e}")
            return False

    async def search_materials(self, telegram_user_id: int, query: str, limit: int = 10) -> List[Dict]:
        """Поиск по материалам (заглушка - endpoint не реализован)."""
        # TODO: Реализовать когда endpoint будет готов
        print(f"Поиск '{query}' пользователем {telegram_user_id}")
        return []

    async def create_user_question(
        self,
        telegram_user_id: int,
        question: str
    ) -> bool:
        """Создать вопрос пользователя через Public API."""
        url = f"{self.base_url}/user-questions"
        data = {"telegram_user_id": telegram_user_id, "question_text": question}
        try:
            async with self.session.post(url, json=data) as response:
                return response.status == 201
        except Exception as e:
            print(f"Ошибка создания вопроса: {e}")
            return False

    async def create_telegram_user(
        self,
        telegram_id: int,
        first_name: str,
        last_name: Optional[str] = None,
        username: Optional[str] = None
    ) -> bool:
        """Создать пользователя через Bot API."""
        url = f"{self.base_url}/telegram-user/register"
        data = {
            "update_id": 1,
            "message": {
                "message_id": 1,
                "from": {"id": telegram_id, "first_name": first_name, "last_name": last_name, "username": username},
                "chat": {"id": telegram_id, "type": "private"},
                "date": 1640995200,
                "text": "/start",
            },
        }

        try:
            async with self.session.post(url, json=data) as response:
                return response.status == 200
        except Exception as e:
            print(f"Ошибка создания пользователя: {e}")
            return False

    async def get_inactive_users(self, days: int) -> Dict:
        """Получить пользователей, которые неактивны <days> дней."""
        url = f"{self.base_url}/reminders/inactive_users"
        query = {"inactive_days": days}
        try:
            async with self.session.get(url, params=query) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Ошибка получения неактивных пользователей: {response.status}")
                    return {"users": []}
        except Exception as e:
            print(f"Ошибка подключения к API: {e}")
            return {"users": []}

    async def get_reminder_template(self) -> Dict:
        """Получить шаблон для рассылки напоминаний."""
        url = f"{self.base_url}/reminders/template"
        try:
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    print(f"Ошибка получения шабона напоминаний: {response.status}")
                    return {}
        except Exception as e:
            print(f"Ошибка подключения к API: {e}")
            return {}
