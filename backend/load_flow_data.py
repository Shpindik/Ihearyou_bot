#!/usr/bin/env python3
"""Скрипт для загрузки данных в соответствии с flow и ссылками с сайта ihearyou.ru."""

import asyncio
import os
import sys
from typing import Any, Dict, List

from sqlalchemy import delete, select


sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.core.db import AsyncSessionLocal
from backend.crud import ContentFileCRUD, MenuItemCRUD
from backend.models.content_file import ContentFile
from backend.models.enums import AccessLevel, ContentType
from backend.models.menu_item import MenuItem


class FlowDataLoader:
    """Класс для загрузки данных в соответствии с flow."""

    def __init__(self):
        """Инициализация загрузчика данных."""
        self.menu_crud = MenuItemCRUD()
        self.content_crud = ContentFileCRUD()

    async def clear_existing_data(self, session):
        """Очистить существующие данные."""
        print("🧹 Очистка существующих данных...")

        # Удаляем все контентные файлы
        await session.execute(delete(ContentFile))

        # Удаляем все пункты меню
        await session.execute(delete(MenuItem))

        await session.commit()
        print("✅ Данные очищены")

    async def create_main_menu_items(self, session):
        """Создать основные пункты меню - 2 динамичные кнопки после /start."""
        print("📋 Создание основных пунктов меню...")

        main_items = [
            {
                "title": "Я волнуюсь о слухе ребенка",
                "description": "Информация и поддержка для родителей детей с нарушением слуха",
                "bot_message": "Понимание ваших беспокойств. Давайте разберем, что вас интересует:",
                "content": "👶 **Поддержка для родителей**\n\nМы понимаем, как важно для вас помочь своему ребенку. На нашем сайте вы найдете:\n\n• **Информацию для родителей** - https://www.ihearyou.ru/\n• **Материалы по развитию** - https://www.ihearyou.ru/\n• **Истории семей** - https://www.ihearyou.ru/\n• **Проверка слуха онлайн** - https://www.ihearyou.ru/\n\n**Контакты для поддержки:**\n📞 +7 911 282 48 55\n📞 +7 921 930 78 63\n📧 info@ihearyou.ru\n\nПодробнее: https://www.ihearyou.ru/",
            },
            {
                "title": "Я волнуюсь о своем слухе",
                "description": "Информация и поддержка для взрослых с нарушением слуха",
                "bot_message": "Понимание ваших беспокойств. Давайте разберем, что вас интересует:",
                "content": "👤 **Поддержка для взрослых**\n\nЕсли вы замечаете проблемы со слухом, важно действовать. На нашем сайте вы найдете:\n\n• **Проверка слуха онлайн** - https://www.ihearyou.ru/\n• **Материалы о слухе** - https://www.ihearyou.ru/\n• **Советы по сохранению слуха** - https://www.ihearyou.ru/\n• **Информацию о слуховых аппаратах** - https://www.ihearyou.ru/\n\n**Контакты для поддержки:**\n📞 +7 911 282 48 55\n📞 +7 921 930 78 63\n📧 info@ihearyou.ru\n\nПодробнее: https://www.ihearyou.ru/",
            },
        ]

        for item_data in main_items:
            # Создаем новый пункт меню
            menu_item = MenuItem(
                title=item_data["title"],
                description=item_data["description"],
                bot_message=item_data["bot_message"],
                parent_id=None,
                is_active=True,
                access_level=AccessLevel.FREE,
            )
            session.add(menu_item)
            await session.flush()  # Получаем ID

            # Создаем контент
            content = ContentFile(
                menu_item_id=menu_item.id,
                content_type=ContentType.TEXT,
                content_text=item_data["content"],
                is_primary=True,
                sort_order=1,
            )
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
                "content": "🔍 **Диагностика слуха у детей**\n\nДля правильной диагностики слуха у детей необходимо:\n\n1. **Аудиометрия** - проверка остроты слуха\n2. **Тимпанометрия** - оценка состояния среднего уха\n3. **Речевая аудиометрия** - проверка разборчивости речи\n4. **Игровая аудиометрия** - для детей младшего возраста\n\nРекомендуется проходить диагностику у специалиста-сурдолога.\n\nПодробнее: https://www.ihearyou.ru/",
            },
            {
                "title": "Слуховые аппараты",
                "description": "Всё о слуховых аппаратах для детей",
                "bot_message": "Выберите раздел о слуховых аппаратах:",
                "content": "🎧 **Слуховые аппараты для детей**\n\n**Типы слуховых аппаратов для детей:**\n\n• **Заушные (BTE)** - мощные, подходят для тяжелых потерь слуха\n• **Внутриушные (ITE)** - компактные, индивидуальные\n• **Внутриканальные (ITC)** - незаметные, для легких потерь\n\n**Современные технологии:**\n- Цифровая обработка звука\n- Шумоподавление\n- Направленные микрофоны\n- Bluetooth подключение\n\nПодробнее: https://www.ihearyou.ru/",
            },
            {
                "title": "Обучение и развитие",
                "description": "Материалы для обучения и развития детей",
                "bot_message": "Выберите раздел обучения:",
                "content": "📚 **Обучение и развитие детей**\n\n**Этапы развития ребенка с нарушением слуха:**\n\n1. **Раннее развитие** - от 0 до 3 лет\n2. **Дошкольный период** - от 3 до 7 лет\n3. **Школьный возраст** - от 7 лет\n\n**Полезные советы:**\n• Начинайте с тихих звуков\n• Практикуйтесь в чтении по губам\n• Используйте слуховой аппарат ежедневно\n• Регулярно посещайте сурдолога\n\nПодробнее: https://www.ihearyou.ru/",
            },
            {
                "title": "Помощь специалиста",
                "description": "Получите консультацию эксперта",
                "bot_message": "Нужна помощь профессионала?",
                "content": "👨‍⚕️ **Помощь специалиста**\n\nНаши специалисты готовы помочь вам:\n\n• Консультации по слуху детей\n• Подбор слуховых аппаратов\n• Реабилитация после кохлеарной имплантации\n• Поддержка родителей\n\n**Контакты:**\n📞 +7 911 282 48 55\n📞 +7 921 930 78 63\n📧 info@ihearyou.ru\n\nПодробнее: https://www.ihearyou.ru/",
            },
        ]

        await self._create_subitems(session, child_item.id, child_subitems)
        print("✅ Подразделы для 'Я волнуюсь о слухе ребенка' созданы")

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
                "content": "🔍 **Проверка слуха онлайн**\n\n**Онлайн-тест слуха:**\n\n• **Быстрая проверка** - 5 минут\n• **Точные результаты** - рекомендации специалиста\n• **Бесплатно** - для всех пользователей\n\n**Симптомы нарушения слуха:**\n• Трудности в понимании речи\n• Частые просьбы повторить\n• Увеличение громкости телевизора\n• Проблемы в шумной обстановке\n\n**Пройдите тест:** https://www.ihearyou.ru/\n\nПодробнее: https://www.ihearyou.ru/",
            },
            {
                "title": "Слуховые аппараты",
                "description": "Всё о слуховых аппаратах для взрослых",
                "bot_message": "Выберите раздел о слуховых аппаратах:",
                "content": "🎧 **Слуховые аппараты для взрослых**\n\n**Типы слуховых аппаратов:**\n\n• **Заушные (BTE)** - мощные, подходят для тяжелых потерь слуха\n• **Внутриушные (ITE)** - компактные, индивидуальные\n• **Внутриканальные (ITC)** - незаметные, для легких потерь\n• **Полностью внутриканальные (CIC)** - максимально скрытые\n\n**Современные технологии:**\n- Цифровая обработка звука\n- Шумоподавление\n- Направленные микрофоны\n- Bluetooth подключение\n\nПодробнее: https://www.ihearyou.ru/",
            },
            {
                "title": "Сохранение слуха",
                "description": "Как сохранить и защитить слух",
                "bot_message": "Узнайте, как сохранить слух:",
                "content": "🛡️ **Сохранение слуха**\n\n**10 советов как сохранить слух:**\n\n1. **Избегайте громких звуков**\n2. **Используйте защитные наушники**\n3. **Ограничьте время в шумной среде**\n4. **Регулярно проверяйте слух**\n5. **Не используйте ватные палочки**\n6. **Лечите ушные инфекции**\n7. **Контролируйте уровень громкости**\n8. **Делайте перерывы в прослушивании**\n9. **Избегайте стресса**\n10. **Ведите здоровый образ жизни**\n\nПодробнее: https://www.ihearyou.ru/",
            },
            {
                "title": "Помощь специалиста",
                "description": "Получите консультацию эксперта",
                "bot_message": "Нужна помощь профессионала?",
                "content": "👨‍⚕️ **Помощь специалиста**\n\nНаши специалисты готовы помочь вам:\n\n• Консультации по слуху\n• Подбор слуховых аппаратов\n• Реабилитация после потери слуха\n• Поддержка и адаптация\n\n**Контакты:**\n📞 +7 911 282 48 55\n📞 +7 921 930 78 63\n📧 info@ihearyou.ru\n\nПодробнее: https://www.ihearyou.ru/",
            },
        ]

        await self._create_subitems(session, adult_item.id, adult_subitems)
        print("✅ Подразделы для 'Я волнуюсь о своем слухе' созданы")

    async def _create_subitems(self, session, parent_id: int, subitems: List[Dict[str, Any]]):
        """Создать подразделы для родительского пункта меню."""
        for subitem_data in subitems:
            # Создаем пункт меню
            menu_item = MenuItem(
                title=subitem_data["title"],
                description=subitem_data["description"],
                bot_message=subitem_data["bot_message"],
                parent_id=parent_id,
                is_active=True,
                access_level=AccessLevel.FREE,
            )
            session.add(menu_item)
            await session.flush()  # Получаем ID

            # Создаем контент
            content = ContentFile(
                menu_item_id=menu_item.id,
                content_type=ContentType.TEXT,
                content_text=subitem_data["content"],
                is_primary=True,
                sort_order=1,
            )
            session.add(content)

        await session.commit()

    async def load_all_data(self):
        """Загрузить все данные."""
        async with AsyncSessionLocal() as session:
            try:
                await self.clear_existing_data(session)
                await self.create_main_menu_items(session)
                await self.create_child_subitems(session)

                print("\n🎉 Все данные успешно загружены!")
                print("\n📊 Статистика:")
                print("• Основных разделов: 2")
                print("• Подразделов: 8")
                print("• Всего пунктов меню: 10")
                print("• Контентных блоков: 10")

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
