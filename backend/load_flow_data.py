#!/usr/bin/env python3
"""
Скрипт для загрузки данных в соответствии с flow и ссылками с сайта ihearyou.ru
"""

import asyncio
from typing import List, Dict, Any

from core.db import AsyncSessionLocal
from crud import MenuItemCRUD, ContentFileCRUD
from models.enums import ContentType, AccessLevel
from models.menu import MenuItem
from models.content_file import ContentFile
from sqlalchemy import delete, select


class FlowDataLoader:
    """Класс для загрузки данных в соответствии с flow."""
    
    def __init__(self):
        self.menu_crud = MenuItemCRUD()
        self.content_crud = ContentFileCRUD()
    
    async def clear_existing_data(self, session):
        """Очистить существующие данные."""
        print("🧹 Очистка существующих данных...")
        
        # Удаляем контент для основных пунктов меню
        await session.execute(
            delete(ContentFile).where(ContentFile.menu_item_id.in_([52, 53, 54, 65]))
        )
        
        # Удаляем подразделы
        await session.execute(
            delete(MenuItem).where(MenuItem.parent_id.in_([52, 53, 54, 65]))
        )
        
        await session.commit()
        print("✅ Данные очищены")
    
    async def create_main_menu_items(self, session):
        """Создать основные пункты меню."""
        print("📋 Создание основных пунктов меню...")
        
        main_items = [
            {
                "title": "Диагноз",
                "description": "Информация о диагностике слуха",
                "bot_message": "Выберите раздел диагностики:",
                "content": "🔍 **Диагностика слуха**\n\nДля правильной диагностики слуха необходимо:\n\n1. **Аудиометрия** - проверка остроты слуха\n2. **Тимпанометрия** - оценка состояния среднего уха\n3. **Речевая аудиометрия** - проверка разборчивости речи\n\nРекомендуется проходить диагностику у специалиста-сурдолога.\n\nПодробнее: https://www.ihearyou.ru/"
            },
            {
                "title": "Слуховые аппараты",
                "description": "Всё о слуховых аппаратах",
                "bot_message": "Выберите раздел о слуховых аппаратах:",
                "content": "🎧 **Слуховые аппараты**\n\n**Типы слуховых аппаратов:**\n\n• **Заушные (BTE)** - мощные, подходят для тяжелых потерь слуха\n• **Внутриушные (ITE)** - компактные, индивидуальные\n• **Внутриканальные (ITC)** - незаметные, для легких потерь\n• **Полностью внутриканальные (CIC)** - максимально скрытые\n\n**Современные технологии:**\n- Цифровая обработка звука\n- Шумоподавление\n- Направленные микрофоны\n- Bluetooth подключение\n\nПодробнее: https://www.ihearyou.ru/"
            },
            {
                "title": "Обучение",
                "description": "Материалы для обучения и адаптации",
                "bot_message": "Выберите раздел обучения:",
                "content": "📚 **Обучение и адаптация**\n\n**Этапы адаптации к слуховому аппарату:**\n\n1. **Первая неделя** - привыкание к звукам\n2. **Вторая неделя** - увеличение времени ношения\n3. **Третий месяц** - полная адаптация\n\n**Полезные советы:**\n• Начинайте с тихих звуков\n• Практикуйтесь в чтении по губам\n• Используйте слуховой аппарат ежедневно\n• Регулярно посещайте сурдолога\n\n**Упражнения для развития слуха:**\n- Слушайте музыку\n- Читайте вслух\n- Практикуйтесь в телефонных разговорах\n\nПодробнее: https://www.ihearyou.ru/"
            },
            {
                "title": "Помощь специалиста",
                "description": "Получите консультацию эксперта",
                "bot_message": "Нужна помощь профессионала?",
                "content": "👨‍⚕️ **Помощь специалиста**\n\nНаши специалисты готовы помочь вам:\n\n• Консультации по слуху\n• Подбор слуховых аппаратов\n• Реабилитация после кохлеарной имплантации\n• Поддержка родителей\n\n**Контакты:**\n📞 +7 911 282 48 55\n📞 +7 921 930 78 63\n📧 info@ihearyou.ru\n\nПодробнее: https://www.ihearyou.ru/"
            }
        ]
        
        for item_data in main_items:
            # Создаем новый пункт меню
            menu_item = MenuItem(
                title=item_data["title"],
                description=item_data["description"],
                bot_message=item_data["bot_message"],
                parent_id=None,
                is_active=True,
                access_level=AccessLevel.FREE
            )
            session.add(menu_item)
            await session.flush()  # Получаем ID
            
            # Создаем контент
            content = ContentFile(
                menu_item_id=menu_item.id,
                content_type=ContentType.TEXT,
                content_text=item_data["content"],
                is_primary=True,
                sort_order=1
            )
            session.add(content)
        
        await session.commit()
        print("✅ Основные пункты меню созданы")
    
    async def create_diagnosis_subitems(self, session):
        """Создать подразделы для 'Диагноз'."""
        print("🔍 Создание подразделов 'Диагноз'...")
        
        # Находим ID пункта "Диагноз"
        diagnosis_item = await session.execute(
            select(MenuItem).where(MenuItem.title == "Диагноз")
        )
        diagnosis_item = diagnosis_item.scalar_one_or_none()
        if not diagnosis_item:
            print("❌ Пункт 'Диагноз' не найден")
            return
        
        subitems = [
            {
                "title": "Как принять диагноз",
                "description": "Информация о принятии диагноза",
                "bot_message": "Принятие диагноза - важный шаг.",
                "content": "💙 **Как принять диагноз**\n\nПринятие диагноза может быть сложным процессом. Важно:\n\n• Дать себе время на осознание\n• Обратиться за поддержкой к специалистам\n• Найти сообщество родителей\n• Изучить доступные ресурсы\n\n**Помните:** Вы не одиноки в этой ситуации.\n\nПодробнее: https://www.ihearyou.ru/"
            },
            {
                "title": "Введение, основные понятия",
                "description": "Основные понятия о слухе",
                "bot_message": "Изучите основы слуха.",
                "content": "📖 **Основные понятия о слухе**\n\n**Как устроен слух:**\n• Наружное ухо - улавливает звуки\n• Среднее ухо - передает звуковые колебания\n• Внутреннее ухо - преобразует звук в нервные импульсы\n• Слуховой нерв - передает сигналы в мозг\n\n**Типы нарушений слуха:**\n• Кондуктивная тугоухость\n• Сенсоневральная тугоухость\n• Смешанная тугоухость\n\nПодробнее: https://www.ihearyou.ru/"
            },
            {
                "title": "Типы нарушений слуха",
                "description": "Классификация нарушений слуха",
                "bot_message": "Информация о типах нарушений",
                "content": "🔊 **Типы нарушений слуха**\n\n**По степени потери слуха:**\n• Легкая (20-40 дБ)\n• Умеренная (41-55 дБ)\n• Умеренно-тяжелая (56-70 дБ)\n• Тяжелая (71-90 дБ)\n• Глубокая (более 90 дБ)\n\n**По локализации:**\n• Односторонняя\n• Двусторонняя\n\nПодробнее: https://www.ihearyou.ru/"
            },
            {
                "title": "Диагностика",
                "description": "Методы диагностики слуха",
                "bot_message": "Как проводится диагностика",
                "content": "🩺 **Диагностика слуха**\n\n**Методы диагностики:**\n\n1. **Аудиометрия**\n   - Тональная аудиометрия\n   - Речевая аудиометрия\n   - Игровая аудиометрия (для детей)\n\n2. **Тимпанометрия**\n   - Оценка функции среднего уха\n   - Выявление патологий\n\n3. **ОАЭ (Отоакустическая эмиссия)**\n   - Скрининг новорожденных\n   - Оценка функции улитки\n\nПодробнее: https://www.ihearyou.ru/"
            }
        ]
        
        await self._create_subitems(session, diagnosis_item.id, subitems)
        print("✅ Подразделы 'Диагноз' созданы")
    
    async def create_hearing_aids_subitems(self, session):
        """Создать подразделы для 'Слуховые аппараты'."""
        print("🎧 Создание подразделов 'Слуховые аппараты'...")
        
        # Находим ID пункта "Слуховые аппараты"
        hearing_aids_item = await session.execute(
            select(MenuItem).where(MenuItem.title == "Слуховые аппараты")
        )
        hearing_aids_item = hearing_aids_item.scalar_one_or_none()
        if not hearing_aids_item:
            print("❌ Пункт 'Слуховые аппараты' не найден")
            return
        
        subitems = [
            {
                "title": "Как проверить работу аппарата",
                "description": "Проверка функциональности слухового аппарата",
                "bot_message": "Регулярно проверяйте ваш аппарат.",
                "content": "🔧 **Как проверить работу аппарата**\n\n**Ежедневная проверка:**\n\n1. **Батарейки**\n   - Проверьте заряд\n   - Замените при необходимости\n\n2. **Внешний осмотр**\n   - Отсутствие повреждений\n   - Чистота корпуса\n\n3. **Звук**\n   - Тест в тихой обстановке\n   - Проверка в шумной среде\n\n4. **Вкладыши**\n   - Чистота и целостность\n   - Правильная установка\n\nПодробнее: https://www.ihearyou.ru/"
            },
            {
                "title": "Как чистить аппарат",
                "description": "Инструкция по чистке слухового аппарата",
                "bot_message": "Чистота - залог долгой службы.",
                "content": "🧽 **Как чистить слуховой аппарат**\n\n**Ежедневный уход:**\n\n1. **Корпус аппарата**\n   - Сухая мягкая ткань\n   - Специальные салфетки\n   - Избегайте влаги\n\n2. **Вкладыши**\n   - Мыльная вода\n   - Мягкая щетка\n   - Тщательная сушка\n\n3. **Фильтры**\n   - Регулярная замена\n   - Проверка засорения\n\n**Важно:** Не используйте спирт или агрессивные средства!\n\nПодробнее: https://www.ihearyou.ru/"
            },
            {
                "title": "Почему аппарат свистит",
                "description": "Причины обратной связи в слуховых аппаратах",
                "bot_message": "Разберемся с проблемой свиста.",
                "content": "🔊 **Почему аппарат свистит**\n\n**Причины обратной связи:**\n\n1. **Неправильная установка**\n   - Слабая посадка вкладыша\n   - Неподходящий размер\n\n2. **Засорение**\n   - Серная пробка\n   - Загрязненные фильтры\n\n3. **Повреждения**\n   - Трещины в корпусе\n   - Износ вкладыша\n\n4. **Настройки**\n   - Слишком высокий уровень усиления\n   - Неправильная программа\n\n**Решение:** Обратитесь к специалисту!\n\nПодробнее: https://www.ihearyou.ru/"
            },
            {
                "title": "Аналоговые и цифровые аппараты",
                "description": "Сравнение типов слуховых аппаратов",
                "bot_message": "Узнайте о различиях.",
                "content": "⚡ **Аналоговые и цифровые аппараты**\n\n**Аналоговые аппараты:**\n• Простота конструкции\n• Низкая стоимость\n• Ограниченные возможности\n• Базовое усиление звука\n\n**Цифровые аппараты:**\n• Современные технологии\n• Высокое качество звука\n• Шумоподавление\n• Направленные микрофоны\n• Bluetooth подключение\n• Автоматические программы\n\n**Рекомендация:** Цифровые аппараты предпочтительнее!\n\nПодробнее: https://www.ihearyou.ru/"
            }
        ]
        
        await self._create_subitems(session, hearing_aids_item.id, subitems)
        print("✅ Подразделы 'Слуховые аппараты' созданы")
    
    async def create_education_subitems(self, session):
        """Создать подразделы для 'Обучение'."""
        print("📚 Создание подразделов 'Обучение'...")
        
        # Находим ID пункта "Обучение"
        education_item = await session.execute(
            select(MenuItem).where(MenuItem.title == "Обучение")
        )
        education_item = education_item.scalar_one_or_none()
        if not education_item:
            print("❌ Пункт 'Обучение' не найден")
            return
        
        subitems = [
            {
                "title": "Жизнь с особенным ребенком",
                "description": "Советы для родителей",
                "bot_message": "Поддержка и понимание.",
                "content": "👨‍👩‍👧‍👦 **Жизнь с особенным ребенком**\n\n**Основные принципы:**\n\n• **Принятие** - любите ребенка таким, какой он есть\n• **Терпение** - развитие требует времени\n• **Поддержка** - ищите помощь специалистов\n• **Общение** - говорите с ребенком\n\n**Практические советы:**\n• Создайте слуховую среду\n• Используйте визуальные подсказки\n• Развивайте речь ежедневно\n• Находите время для игр\n\nПодробнее: https://www.ihearyou.ru/"
            },
            {
                "title": "РКС - школа для родителей",
                "description": "Ресурсы для родителей",
                "bot_message": "Образование для родителей.",
                "content": "🏫 **РКС - школа для родителей**\n\n**Что мы предлагаем:**\n\n• **Курсы для родителей**\n  - Основы слуха\n  - Развитие речи\n  - Адаптация к аппарату\n\n• **Групповые занятия**\n  - Обмен опытом\n  - Поддержка сообщества\n  - Совместные активности\n\n• **Индивидуальные консультации**\n  - Персональный подход\n  - Решение конкретных задач\n\n**Присоединяйтесь к нашему сообществу!**\n\nПодробнее: https://www.ihearyou.ru/"
            },
            {
                "title": "Адаптация к особенностям",
                "description": "Как помочь ребенку адаптироваться",
                "bot_message": "Поможем ребенку адаптироваться.",
                "content": "🌟 **Адаптация к особенностям**\n\n**Этапы адаптации:**\n\n1. **Принятие**\n   - Понимание особенностей\n   - Работа с эмоциями\n\n2. **Обучение**\n   - Изучение методов развития\n   - Практические навыки\n\n3. **Интеграция**\n   - Включение в общество\n   - Социальные навыки\n\n**Важно:** Каждый ребенок уникален!\n\nПодробнее: https://www.ihearyou.ru/"
            },
            {
                "title": "Уход за слуховым аппаратом",
                "description": "Правильный уход за аппаратом",
                "bot_message": "Правильный уход продлит срок службы.",
                "content": "🛠️ **Уход за слуховым аппаратом**\n\n**Ежедневный уход:**\n\n• **Очистка**\n  - Сухая мягкая ткань\n  - Специальные средства\n  - Избегайте влаги\n\n• **Хранение**\n  - Сухое место\n  - Защита от пыли\n  - Правильная температура\n\n• **Батарейки**\n  - Проверка заряда\n  - Своевременная замена\n  - Правильное хранение\n\n**Результат:** Долгая и надежная работа!\n\nПодробнее: https://www.ihearyou.ru/"
            }
        ]
        
        await self._create_subitems(session, education_item.id, subitems)
        print("✅ Подразделы 'Обучение' созданы")
    
    async def create_specialist_help_subitems(self, session):
        """Создать подразделы для 'Помощь специалиста'."""
        print("👨‍⚕️ Создание подразделов 'Помощь специалиста'...")
        
        # Находим ID пункта "Помощь специалиста"
        specialist_item = await session.execute(
            select(MenuItem).where(MenuItem.title == "Помощь специалиста")
        )
        specialist_item = specialist_item.scalar_one_or_none()
        if not specialist_item:
            print("❌ Пункт 'Помощь специалиста' не найден")
            return
        
        subitems = [
            {
                "title": "Как проверить слух ребенка",
                "description": "Методы проверки слуха у детей",
                "bot_message": "Ранняя диагностика важна.",
                "content": "👶 **Как проверить слух ребенка**\n\n**Возрастные особенности:**\n\n• **0-6 месяцев**\n  - Рефлекторные реакции\n  - Поведенческие тесты\n\n• **6-18 месяцев**\n  - Игровая аудиометрия\n  - Визуальное подкрепление\n\n• **18+ месяцев**\n  - Условно-рефлекторная аудиометрия\n  - Речевые тесты\n\n**Важно:** Регулярные проверки слуха!\n\nПодробнее: https://www.ihearyou.ru/"
            },
            {
                "title": "Ошибки, чего избегать",
                "description": "Распространенные ошибки родителей",
                "bot_message": "Избегайте типичных ошибок.",
                "content": "⚠️ **Ошибки, чего избегать**\n\n**Частые ошибки родителей:**\n\n• **Отрицание проблемы**\n  - Игнорирование симптомов\n  - Откладывание визита к врачу\n\n• **Неправильные ожидания**\n  - Слишком высокие требования\n  - Нетерпение в развитии\n\n• **Изоляция ребенка**\n  - Ограничение общения\n  - Гиперопека\n\n• **Игнорирование специалистов**\n  - Самолечение\n  - Неследование рекомендациям\n\n**Помните:** Профессиональная помощь важна!\n\nПодробнее: https://www.ihearyou.ru/"
            },
            {
                "title": "Контакты специалистов",
                "description": "Как связаться с экспертами",
                "bot_message": "Мы всегда готовы помочь.",
                "content": "📞 **Контакты специалистов**\n\n**Свяжитесь с нами:**\n\n• **Телефон:**\n  +7 911 282 48 55\n  +7 921 930 78 63\n\n• **Email:**\n  info@ihearyou.ru\n\n• **Адрес:**\n  Россия, г. Санкт-Петербург,\n  ул. Варшавская, 23-2-306\n\n• **Время работы:**\n  Пн-Пт: 9:00-18:00\n  Сб-Вс: по договоренности\n\n**Мы поможем вам!**\n\nПодробнее: https://www.ihearyou.ru/"
            }
        ]
        
        await self._create_subitems(session, specialist_item.id, subitems)
        print("✅ Подразделы 'Помощь специалиста' созданы")
    
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
                access_level=AccessLevel.FREE
            )
            session.add(menu_item)
            await session.flush()  # Получаем ID
            
            # Создаем контент
            content = ContentFile(
                menu_item_id=menu_item.id,
                content_type=ContentType.TEXT,
                content_text=subitem_data["content"],
                is_primary=True,
                sort_order=1
            )
            session.add(content)
        
        await session.commit()
    
    async def load_all_data(self):
        """Загрузить все данные."""
        async with AsyncSessionLocal() as session:
            try:
                await self.clear_existing_data(session)
                await self.create_main_menu_items(session)
                await self.create_diagnosis_subitems(session)
                await self.create_hearing_aids_subitems(session)
                await self.create_education_subitems(session)
                await self.create_specialist_help_subitems(session)
                
                print("\n🎉 Все данные успешно загружены!")
                print("\n📊 Статистика:")
                print(f"• Основных разделов: 4")
                print(f"• Подразделов: 15")
                print(f"• Всего пунктов меню: 19")
                print(f"• Контентных блоков: 19")
                
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
