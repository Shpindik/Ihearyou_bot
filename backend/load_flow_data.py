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
from backend.models.user_activity import UserActivity


class FlowDataLoader:
    """Класс для загрузки данных в соответствии с flow."""

    def __init__(self):
        """Инициализация загрузчика данных."""
        self.menu_crud = MenuItemCRUD()
        self.content_crud = ContentFileCRUD()

    async def clear_existing_data(self, session):
        """Очистить существующие данные."""
        print("🧹 Очистка существующих данных...")

        # Удаляем активности пользователей (чтобы избежать конфликтов внешних ключей)
        await session.execute(delete(UserActivity))

        # Удаляем все контентные файлы
        await session.execute(delete(ContentFile))

        # Удаляем все пункты меню
        await session.execute(delete(MenuItem))

        await session.commit()
        print("✅ Данные очищены")

    async def create_main_menu_items(self, session):
        """Создать основные пункты меню - 2 динамичные кнопки после /start."""
        main_items = [
            {
                "title": "Я волнуюсь о слухе ребенка",
                "description": "Информация и поддержка для родителей детей с нарушением слуха",
                "bot_message": "Понимаю твоё волнение 💙 Давай разберёмся вместе!\n\nВыбери, что тебя интересует:",
                "content": "👶 **Поддержка для родителей**\n\nМы понимаем, как важно для вас помочь своему ребенку. На нашем сайте вы найдете:\n\n• **Информацию для родителей** - https://www.ihearyou.ru/\n• **Материалы по развитию** - https://www.ihearyou.ru/\n• **Истории семей** - https://www.ihearyou.ru/\n• **Проверка слуха онлайн** - https://www.ihearyou.ru/\n\n**Контакты для поддержки:**\n📞 +7 911 282 48 55\n📞 +7 921 930 78 63\n📧 info@ihearyou.ru\n\nПодробнее: https://www.ihearyou.ru/",
            },
            {
                "title": "Я волнуюсь о своем слухе",
                "description": "Информация и поддержка для взрослых с нарушением слуха",
                "bot_message": "Не переживай, ты не один с такими мыслями 💙 \n\nВыбери, что тебя интересует сейчас, а я помогу тебе с этим разобраться 😊",
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

    async def create_child_subitems(self, session):
        """Создать подразделы для основных пунктов меню."""
        # Находим ID пункта "Я волнуюсь о слухе ребенка"
        child_item = await session.execute(
            select(MenuItem).where(MenuItem.title == "Я волнуюсь о слухе ребенка").limit(1)
        )
        child_item = child_item.first()
        if not child_item:
            return

        child_item = child_item[0]  # Получаем объект из кортежа

        child_subitems = [
            {
                "title": "Проверить слух ребёнка",
                "description": "Информация и материалы по проверке слуха у детей",
                "bot_message": "Я понимаю твои переживания о слухе у ребёнка и хочу помочь 💙 \n\nВот информация, которая поможет лучше разобраться в ситуации.",
                "content": "🔍 **Проверка слуха у ребёнка**\n\nПолезные материалы о том, как понять, как слышит ребёнок, и как проходит проверка слуха.",
            },
            {
                "title": "Мы только узнали о снижении слуха ребенка",
                "description": "Поддержка в первые дни после новости",
                "bot_message": "Я понимаю, как тяжело может быть получить такую новость 💙 Давай поговорим, как справиться с эмоциями и что делать на первых этапах, чтобы помочь ребёнку чувствовать себя комфортно.",
                "content": "💙 **Первые шаги и поддержка**\n\nМатериалы о поддержке семьи и ребёнка на старте пути.",
            },
            {
                "title": "Жизнь со слуховыми особенностями",
                "description": "Как жить и развиваться со слуховыми особенностями",
                "bot_message": "Хочу рассказать тебе больше о жизни детей с нарушением слуха 💛 Я собрал информацию на разные темы, которая поможет облегчить каждый день тебе и твоему ребёнку.",
                "content": "💙 **Жизнь со слуховыми особенностями**\n\nПодборка материалов для повседневной жизни и развития.",
            },
        ]

        created_child_items = {}
        for subitem_data in child_subitems:
            menu_item = MenuItem(
                title=subitem_data["title"],
                description=subitem_data["description"],
                bot_message=subitem_data["bot_message"],
                parent_id=child_item.id,
                is_active=True,
                access_level=AccessLevel.FREE,
            )
            session.add(menu_item)
            await session.flush()

            content = ContentFile(
                menu_item_id=menu_item.id,
                content_type=ContentType.TEXT,
                content_text=subitem_data["content"],
                is_primary=True,
                sort_order=1,
            )
            session.add(content)

            created_child_items[subitem_data["title"]] = menu_item

        await session.commit()

        # Под-подразделы для "Проверить слух ребёнка"
        if "Проверить слух ребёнка" in created_child_items:
            check_child_hearing_item = created_child_items["Проверить слух ребёнка"]

            check_child_links = [
                {
                    "title": "Подкаст: как понять, как слышит ребёнок?",
                    "description": "Подкаст об аудиограмме",
                    "bot_message": child_subitems[0]["bot_message"],
                    "content": "Материал на сайте ihearyou.ru",
                    "web_app_url": "https://www.ihearyou.ru/materials/articles/vypusk-podkasta-ne-ponaslyshke-audiogramma",
                },
                {
                    "title": "Как проходит проверка слуха у ребёнка",
                    "description": "Статья о проверке слуха у детей",
                    "bot_message": child_subitems[0]["bot_message"],
                    "content": "Материал на сайте ihearyou.ru",
                    "web_app_url": "https://www.ihearyou.ru/materials/articles/ya-volnuyus-o-slukhe-svoego-rebenka",
                },
            ]

            for link in check_child_links:
                menu_item = MenuItem(
                    title=link["title"],
                    description=link["description"],
                    bot_message=link["bot_message"],
                    web_app_url=link.get("web_app_url"),
                    parent_id=check_child_hearing_item.id,
                    is_active=True,
                    access_level=AccessLevel.FREE,
                )
                session.add(menu_item)
                await session.flush()

                content = ContentFile(
                    menu_item_id=menu_item.id,
                    content_type=ContentType.TEXT,
                    content_text=link["content"],
                    is_primary=True,
                    sort_order=1,
                )
                session.add(content)

            await session.commit()

        # Под-подразделы для "Мы только узнали о снижении слуха ребенка"
        if "Мы только узнали о снижении слуха ребенка" in created_child_items:
            just_learned_item = created_child_items["Мы только узнали о снижении слуха ребенка"]

            just_learned_subitems = [
                {
                    "title": "Поддержка и первые шаги",
                    "description": "Советы и первые действия",
                    "bot_message": "Давай разберёмся вместе, как поддержать ребёнка и какие первые шаги сделать",
                    "content": "💙 **Поддержка и первые шаги**\n\nМатериалы для старта пути.",
                },
                {
                    "title": "Эмоции и принятие",
                    "description": "Как справляться с эмоциями",
                    "bot_message": "Понимаю тебя 💛\n\nДавай поговорим о том, как справляться с эмоциями и принять ситуацию спокойно.",
                    "content": "💛 **Эмоции и принятие**\n\nМатериалы для поддержки родителей.",
                },
            ]

            created_just_learned = {}
            for subitem_data in just_learned_subitems:
                menu_item = MenuItem(
                    title=subitem_data["title"],
                    description=subitem_data["description"],
                    bot_message=subitem_data["bot_message"],
                    parent_id=just_learned_item.id,
                    is_active=True,
                    access_level=AccessLevel.FREE,
                )
                session.add(menu_item)
                await session.flush()

                content = ContentFile(
                    menu_item_id=menu_item.id,
                    content_type=ContentType.TEXT,
                    content_text=subitem_data["content"],
                    is_primary=True,
                    sort_order=1,
                )
                session.add(content)

                created_just_learned[subitem_data["title"]] = menu_item

            await session.commit()

        # Под-подразделы для "Жизнь со слуховыми особенностями"
        if "Жизнь со слуховыми особенностями" in created_child_items:
            life_item = created_child_items["Жизнь со слуховыми особенностями"]

            life_subitems = [
                {
                    "title": "Поддержка в школе и общении",
                    "description": "Материалы для школы и коммуникации",
                    "bot_message": "Я подготовил для тебя полезную информацию о жизни ребёнка в школе и с друзьями 👩‍🏫👫\n\nДавай вместе разберёмся с проблемами, которые могут возникнуть!",
                    "content": "👩‍🏫 **Поддержка в школе и общении**\n\nПодборка материалов для школы и общения.",
                },
                {
                    "title": "Слуховые протезы",
                    "description": "Кохлеарные импланты и слуховые аппараты",
                    "bot_message": "Слуховые протезы — отличные помощники для твоего ребёнка.\n\nДавай разберёмся, какие они бывают и как правильно с ними обращаться.",
                    "content": "🎧 **Слуховые протезы**\n\nИнформация об устройстве, подборе и уходе.",
                },
                {
                    "title": "Советы психолога",
                    "description": "Психологическая поддержка семьи",
                    "bot_message": "Я собрал информацию, которая поможет понять психологическое состояние твоего ребёнка 😊\n\nДавай обратим внимание на советы профессионалов — они точно знают, как помочь!",
                    "content": "🧠 **Советы психолога**\n\nМатериалы по психологии и отношениям.",
                },
                {
                    "title": "Юридическая информация",
                    "description": "Права и льготы",
                    "bot_message": "Юридическая сторона тоже важна. Хочу рассказать тебе о твоих правах и о том, как государство помогает детям с нарушениями слуха. Уверен, эта информация будет полезна!",
                    "content": "⚖️ **Юридическая информация**\n\nСобрание документов и льгот.",
                },
            ]

            created_life_items = {}
            for subitem_data in life_subitems:
                menu_item = MenuItem(
                    title=subitem_data["title"],
                    description=subitem_data["description"],
                    bot_message=subitem_data["bot_message"],
                    parent_id=life_item.id,
                    is_active=True,
                    access_level=AccessLevel.FREE,
                )
                session.add(menu_item)
                await session.flush()

                content = ContentFile(
                    menu_item_id=menu_item.id,
                    content_type=ContentType.TEXT,
                    content_text=subitem_data["content"],
                    is_primary=True,
                    sort_order=1,
                )
                session.add(content)

                created_life_items[subitem_data["title"]] = menu_item

            await session.commit()

            # Ссылки: Поддержка в школе и общении
            if "Поддержка в школе и общении" in created_life_items:
                school_comm_item = created_life_items["Поддержка в школе и общении"]

                school_links = [
                    {
                        "title": "Как общаться со слабослышащими людьми",
                        "description": "Рекомендации по общению",
                        "bot_message": life_subitems[0]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/kak-obshchatsya-so-slaboslyshashchimi-lyudmi",
                    },
                    {
                        "title": "Инклюзия в школе: как помочь ребёнку",
                        "description": "Инклюзивная среда",
                        "bot_message": life_subitems[0]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/inclusion/",
                    },
                    {
                        "title": "Книга для учителей",
                        "description": "Ребенок с нарушенным слухом в массовой школе",
                        "bot_message": life_subitems[0]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/o-potrebnostyakh-i-osobennostyakh-detey-s-narushennym-slukhom/kniga-rebenok-s-narushennym-slukhom-v-massovoy-shkole-samoe-vazhnoe-chto-dolzhen-znat-uchitel",
                    },
                    {
                        "title": "Онлайн-курс для учителей",
                        "description": "Пусть каждый ребенок услышит",
                        "bot_message": life_subitems[0]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/obrazovanie/obuchayushchiy-igrovoy-onlayn-kurs-pust-kazhdyy-rebenok-uslyshit",
                    },
                ]

                for link in school_links:
                    menu_item = MenuItem(
                        title=link["title"],
                        description=link["description"],
                        bot_message=link["bot_message"],
                        web_app_url=link.get("web_app_url"),
                        parent_id=school_comm_item.id,
                        is_active=True,
                        access_level=AccessLevel.FREE,
                    )
                    session.add(menu_item)
                    await session.flush()

                    content = ContentFile(
                        menu_item_id=menu_item.id,
                        content_type=ContentType.TEXT,
                        content_text=link["content"],
                        is_primary=True,
                        sort_order=1,
                    )
                    session.add(content)

            # Ссылки: Слуховые протезы
            if "Слуховые протезы" in created_life_items:
                prostheses_item = created_life_items["Слуховые протезы"]

                prostheses_links = [
                    {
                        "title": "Кохлеарные импланты: ответы на частые вопросы",
                        "description": "FAQ по КИ",
                        "bot_message": life_subitems[1]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/chto-takoe-kohlearnaya-implantatsiya",
                    },
                    {
                        "title": "Умение говорить в слуховых аппаратах",
                        "description": "Развитие речи",
                        "bot_message": life_subitems[1]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/kak-razvivat-u-rebyenka-umenie-govorit-v-slukhovykh-apparatakh",
                    },
                    {
                        "title": "Что такое кохлеарная имплантация?",
                        "description": "Обзор КИ",
                        "bot_message": life_subitems[1]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/chto-takoe-kokhlearnaya-implantatsiya",
                    },
                    {
                        "title": "Как правильно надеть аппарат",
                        "description": "Инструкция",
                        "bot_message": life_subitems[1]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/kak-pravilno-nadet-slukhovoy-apparat",
                    },
                    {
                        "title": "Как проверить, работает ли слуховой аппарат",
                        "description": "Проверка работы СА",
                        "bot_message": life_subitems[1]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/kak-proverit-rabotaet-li-slukhovoy-apparat",
                    },
                    {
                        "title": "Уход за ушным вкладышем",
                        "description": "Гигиена и уход",
                        "bot_message": life_subitems[1]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/ukhod-za-ushnym-vkladyshem",
                    },
                    {
                        "title": "Почему аппарат может свистеть",
                        "description": "Типичные причины",
                        "bot_message": life_subitems[1]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/pochemu-slukhovoy-apparat-svistit",
                    },
                ]

                for link in prostheses_links:
                    menu_item = MenuItem(
                        title=link["title"],
                        description=link["description"],
                        bot_message=link["bot_message"],
                        web_app_url=link.get("web_app_url"),
                        parent_id=prostheses_item.id,
                        is_active=True,
                        access_level=AccessLevel.FREE,
                    )
                    session.add(menu_item)
                    await session.flush()

                    content = ContentFile(
                        menu_item_id=menu_item.id,
                        content_type=ContentType.TEXT,
                        content_text=link["content"],
                        is_primary=True,
                        sort_order=1,
                    )
                    session.add(content)

            # Ссылки: Советы психолога
            if "Советы психолога" in created_life_items:
                psych_item = created_life_items["Советы психолога"]

                psych_links = [
                    {
                        "title": "Подростки: психологические последствия снижения слуха",
                        "description": "Последствия у подростков",
                        "bot_message": life_subitems[2]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/o-potrebnostyakh-i-osobennostyakh-detey-s-narushennym-slukhom/psikhologicheskie-posledstviya-narusheniya-slukha-u-podrostkov",
                    },
                    {
                        "title": "Особенности психического здоровья слабослышащих детей",
                        "description": "Ментальное здоровье",
                        "bot_message": life_subitems[2]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/pochemu-vazhno-znat-ob-osobennostyakh-mentalnogo-zdorovya-glukhikh-i-slaboslyshashchikh-detei",
                    },
                    {
                        "title": "Как потеря слуха отражается на семье",
                        "description": "Влияние на семью",
                        "bot_message": life_subitems[2]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/vliyanie-poteri-slukha-na-semyu",
                    },
                    {
                        "title": "12 стратегий: Как выстраивать отношения с ребёнком",
                        "description": "Стратегии отношений",
                        "bot_message": life_subitems[2]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/12-strategiy-sozdaniya-khoroshikh-vzaimootnosheniy-roditelya-i-rebenka",
                    },
                    {
                        "title": "Игры: учим малыша слышать и говорить",
                        "description": "Игры для развития",
                        "bot_message": life_subitems[2]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://ihearyou.ru/materials/uchim-malysha-slyshat-i-govorit/uchim-malisha-slyshat-i-govorit",
                    },
                    {
                        "title": "Что нужно знать о братьях и сестрах",
                        "description": "О сиблингах",
                        "bot_message": life_subitems[2]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/chto-roditelyam-nado-znat-o-bratyakh-i-syestrakh",
                    },
                ]

                for link in psych_links:
                    menu_item = MenuItem(
                        title=link["title"],
                        description=link["description"],
                        bot_message=link["bot_message"],
                        web_app_url=link.get("web_app_url"),
                        parent_id=psych_item.id,
                        is_active=True,
                        access_level=AccessLevel.FREE,
                    )
                    session.add(menu_item)
                    await session.flush()

                    content = ContentFile(
                        menu_item_id=menu_item.id,
                        content_type=ContentType.TEXT,
                        content_text=link["content"],
                        is_primary=True,
                        sort_order=1,
                    )
                    session.add(content)

            # Ссылки: Юридическая информация
            if "Юридическая информация" in created_life_items:
                legal_item = created_life_items["Юридическая информация"]

                legal_links = [
                    {
                        "title": "Документы и льготы для семей",
                        "description": "Юр. документы и льготы",
                        "bot_message": life_subitems[3]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/skachat/yuridicheskaya-informatsiya",
                    },
                    {
                        "title": "Декларация прав родителей",
                        "description": "Права родителей",
                        "bot_message": life_subitems[3]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/deklaratsia-prav-roditeley",
                    },
                ]

                for link in legal_links:
                    menu_item = MenuItem(
                        title=link["title"],
                        description=link["description"],
                        bot_message=link["bot_message"],
                        web_app_url=link.get("web_app_url"),
                        parent_id=legal_item.id,
                        is_active=True,
                        access_level=AccessLevel.FREE,
                    )
                    session.add(menu_item)
                    await session.flush()

                    content = ContentFile(
                        menu_item_id=menu_item.id,
                        content_type=ContentType.TEXT,
                        content_text=link["content"],
                        is_primary=True,
                        sort_order=1,
                    )
                    session.add(content)

            await session.commit()
            # Ссылки для "Поддержка и первые шаги"
            if "Поддержка и первые шаги" in created_just_learned:
                support_first_steps_item = created_just_learned["Поддержка и первые шаги"]

                support_links = [
                    {
                        "title": "Как справиться с паникой и где искать информацию после постановки диагноза",
                        "description": "Памятка для родителей",
                        "bot_message": just_learned_subitems[0]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/kak-nachinat",
                    },
                    {
                        "title": "Советы от родителей, которые уже прошли через это",
                        "description": "Опыт родителей",
                        "bot_message": just_learned_subitems[0]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://ihearyou.ru/materials/skoraya-pomoshch-ot-roditeley-roditelyam/skoraya-pomoshch-ot-roditeley-roditelyam",
                    },
                    {
                        "title": "Первые шаги: общение и слухопротезирование",
                        "description": "Что делать далее",
                        "bot_message": just_learned_subitems[0]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/pervye-shagi-kommunikatsiya-slukhoprotezirovanie",
                    },
                ]

                for link in support_links:
                    menu_item = MenuItem(
                        title=link["title"],
                        description=link["description"],
                        bot_message=link["bot_message"],
                        web_app_url=link.get("web_app_url"),
                        parent_id=support_first_steps_item.id,
                        is_active=True,
                        access_level=AccessLevel.FREE,
                    )
                    session.add(menu_item)
                    await session.flush()

                    content = ContentFile(
                        menu_item_id=menu_item.id,
                        content_type=ContentType.TEXT,
                        content_text=link["content"],
                        is_primary=True,
                        sort_order=1,
                    )
                    session.add(content)

            # Ссылки для "Эмоции и принятие"
            if "Эмоции и принятие" in created_just_learned:
                emotions_item = created_just_learned["Эмоции и принятие"]

                emotions_links = [
                    {
                        "title": "С чего начать, когда узнали о снижении слуха",
                        "description": "С чего начать",
                        "bot_message": just_learned_subitems[1]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/kak-nachinat",
                    },
                    {
                        "title": "Как принять диагноз: история слонёнка Дамбо",
                        "description": "История принятия",
                        "bot_message": just_learned_subitems[1]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/kak-prinyat-diagnoz-istoriya-slonyenka-dambo",
                    },
                    {
                        "title": "Как потеря слуха влияет на семью",
                        "description": "О влиянии на семью",
                        "bot_message": just_learned_subitems[1]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/vliyanie-poteri-slukha-na-semyu",
                    },
                ]

                for link in emotions_links:
                    menu_item = MenuItem(
                        title=link["title"],
                        description=link["description"],
                        bot_message=link["bot_message"],
                        web_app_url=link.get("web_app_url"),
                        parent_id=emotions_item.id,
                        is_active=True,
                        access_level=AccessLevel.FREE,
                    )
                    session.add(menu_item)
                    await session.flush()

                    content = ContentFile(
                        menu_item_id=menu_item.id,
                        content_type=ContentType.TEXT,
                        content_text=link["content"],
                        is_primary=True,
                        sort_order=1,
                    )
                    session.add(content)

            await session.commit()

        # Находим ID пункта "Я волнуюсь о своем слухе"
        adult_item = await session.execute(
            select(MenuItem).where(MenuItem.title == "Я волнуюсь о своем слухе").limit(1)
        )
        adult_item = adult_item.first()
        if not adult_item:
            print("❌ Пункт 'Я волнуюсь о своем слухе' не найден")
            return

        adult_item = adult_item[0]  # Получаем объект из кортежа

        # Создаем подразделы для "Я волнуюсь о своем слухе"
        adult_subitems = [
            {
                "title": "Замечаю проблемы со слухом",
                "description": "Что делать если есть проблемы со слухом",
                "bot_message": "Спасибо, что поделился 🙏 Хочешь проверить свой слух или узнать больше о симптомах?",
                "content": "👂 **Проблемы со слухом**\n\nЕсли вы заметили проблемы со слухом, важно не откладывать и обратиться за помощью:\n\n**Распространенные признаки:**\n• Трудности в понимании речи собеседника\n• Просьбы повторить сказанное\n• Увеличение громкости телевизора или радио\n• Проблемы с восприятием в шумных местах\n• Звон или шум в ушах\n\n**Что делать:**\n1. **Пройдите онлайн-тест** слуха на нашем сайте\n2. **Обратитесь к специалисту** для профессиональной диагностики\n3. **Не игнорируйте проблему** - раннее выявление важно\n\n**Бесплатная консультация:**\n📞 +7 911 282 48 55\n📞 +7 921 930 78 63\n📧 info@ihearyou.ru\n\nПодробнее: https://www.ihearyou.ru/",
            },
            {
                "title": "Хочу узнать про заботу о слухе",
                "description": "Как правильно заботиться о своем слухе",
                "bot_message": "Классно, что ты думаешь о профилактике 🙌 \n\nХочешь узнать, как сохранить слух, или почитать о жизни с особенностями слуха?",
                "content": "🛡️ **Забота о слухе**\n\n**Ежедневные правила ухода за слухом:**\n\n**✅ Что нужно делать:**\n• Регулярно проверять слух (минимум 1 раз в год)\n• Использовать защитные наушники в шумных местах\n• Делать перерывы при длительном прослушивании музыки\n• Поддерживать здоровый образ жизни\n• Лечить простудные заболевания timely\n\n**❌ Чего избегать:**\n• Громкой музыки в наушниках (>85 дБ)\n• Использования ватных палочек для чистки ушей\n• Игнорирования симптомов нарушения слуха\n• Длительного пребывания в очень шумных местах\n\n**Профилактика:**\n• Сбалансированное питание богатое витаминами\n• Регулярные физические упражнения\n• Избегание стресса и переутомления\n• Контроль уровня холестерина и артериального давления\n\nПодробнее: https://www.ihearyou.ru/",
            },
        ]

        # Создаем подразделы
        created_items = {}
        for subitem_data in adult_subitems:
            # Создаем пункт меню
            menu_item = MenuItem(
                title=subitem_data["title"],
                description=subitem_data["description"],
                bot_message=subitem_data["bot_message"],
                parent_id=adult_item.id,
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

            # Сохраняем созданный элемент для дальнейшего использования
            created_items[subitem_data["title"]] = menu_item

        await session.commit()

        # Теперь создаем под-подразделы для "Замечаю проблемы со слухом"
        if "Замечаю проблемы со слухом" in created_items:
            hearing_problems_item = created_items["Замечаю проблемы со слухом"]

            hearing_problems_subitems = [
                {
                    "title": "Проверить слух",
                    "description": "Проверить свой слух онлайн или узнать больше",
                    "bot_message": "Спасибо, что поделился 🙏\n\nХочешь проверить свой слух или узнать больше о симптомах?",
                    "content": "🔍 **Проверка слуха**\n\nВыберите удобный способ проверки вашего слуха:\n\n• **Онлайн-тест** - быстрый способ проверить слух самостоятельно\n• **Статья с советами** - полезная информация о проверке слуха\n• **Консультация специалиста** - профессиональная диагностика\n\nНе откладывайте - ранняя диагностика важна для сохранения слуха!",
                },
                {
                    "title": "Узнать о симптомах",
                    "description": "Информация о признаках проблем со слухом",
                    "bot_message": "Вот подсказки, на какие сигналы стоит обратить внимание 👂 Но не переживай: это только для ориентира. Если будут сомнения — лучше обратиться к специалисту.",
                    "content": "👂 **Симптомы проблем со слухом**\n\nОбратите внимание на эти признаки:\n\n**Слуховые симптомы:**\n• Трудности в понимании речи\n• Просьбы повторить сказанное\n• Увеличение громкости устройств\n• Проблемы в шумных местах\n• Звон или шум в ушах\n\n**Другие признаки:**\n• Частые головные боли\n• Проблемы с равновесием\n• Чувство давления в ушах\n• Выделения из ушей\n\nЕсли заметили несколько симптомов - обязательно проконсультируйтесь со специалистом!",
                },
            ]

            created_subitems = {}
            for subitem_data in hearing_problems_subitems:
                menu_item = MenuItem(
                    title=subitem_data["title"],
                    description=subitem_data["description"],
                    bot_message=subitem_data["bot_message"],
                    parent_id=hearing_problems_item.id,
                    is_active=True,
                    access_level=AccessLevel.FREE,
                )
                session.add(menu_item)
                await session.flush()

                content = ContentFile(
                    menu_item_id=menu_item.id,
                    content_type=ContentType.TEXT,
                    content_text=subitem_data["content"],
                    is_primary=True,
                    sort_order=1,
                )
                session.add(content)

                created_subitems[subitem_data["title"]] = menu_item

            await session.commit()

            # Создаем под-под-подразделы для "Проверить слух"
            if "Проверить слух" in created_subitems:
                check_hearing_item = created_subitems["Проверить слух"]

                check_hearing_subitems = [
                    {
                        "title": "Онлайн тест слуха",
                        "description": "Быстрый онлайн-тест для проверки слуха",
                        "bot_message": "Готов проверить слух прямо сейчас? Запусти онлайн-тест или изучите статью с полезными советами.",
                        "content": "🔊 **Онлайн тест слуха**\n\nПройдите простой и быстрый тест для предварительной оценки вашего слуха.\n\nТест поможет:\n• Определить возможные проблемы со слухом\n• Получить рекомендации по дальнейшим действиям\n• Узнать о необходимости профессиональной диагностики\n\n**Время прохождения:** 3-5 минут\n**Результат:** Рекомендации специалиста\n\nЗапустите тест прямо сейчас!",
                        "web_app_url": "https://hearing.ru/i-hear-you/",
                    },
                    {
                        "title": "Статья с советами",
                        "description": "Полезная статья о проверке слуха",
                        "bot_message": "Готов проверить слух прямо сейчас😁? Запусти онлайн-тест или изучите статью с полезными советами🧐",
                        "content": "📖 **Статья о проверке слуха**\n\nПрочитайте подробную статью о том, почему важно регулярно проверять слух и как это делать правильно.\n\nВ статье вы найдете:\n• 8 причин для регулярной проверки слуха\n• Как подготовиться к проверке\n• Что делать после получения результатов\n• Советы по сохранению слуха\n\nПолезная информация для заботы о вашем слухе!",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/8-prichin-postavit-proverku-slukha-na-pervoe-mesto-v-spiske-vashikh-del",
                    },
                ]

                for subitem_data in check_hearing_subitems:
                    menu_item = MenuItem(
                        title=subitem_data["title"],
                        description=subitem_data["description"],
                        bot_message=subitem_data["bot_message"],
                        web_app_url=subitem_data.get("web_app_url"),
                        parent_id=check_hearing_item.id,
                        is_active=True,
                        access_level=AccessLevel.FREE,
                    )
                    session.add(menu_item)
                    await session.flush()

                    content = ContentFile(
                        menu_item_id=menu_item.id,
                        content_type=ContentType.TEXT,
                        content_text=subitem_data["content"],
                        is_primary=True,
                        sort_order=1,
                    )
                    session.add(content)

            # Создаем под-под-подразделы для "Узнать о симптомах"
            if "Узнать о симптомах" in created_subitems:
                symptoms_item = created_subitems["Узнать о симптомах"]

                symptoms_subitems = [
                    {
                        "title": "Звон в ушах: что это значит?",
                        "description": "Информация о тиннитусе и его причинах",
                        "bot_message": "Вот подсказки, на какие сигналы стоит обратить внимание 🧐\n\nНо не переживай: это только для ориентира. Если будут сомнения — лучше обратиться к специалисту.",
                        "content": "🔊 **Звон в ушах (тиннитус)**\n\nТиннитус - это звон, жужжание или другие звуки в ушах без внешнего источника.\n\n**Возможные причины:**\n• Повреждение слухового нерва\n• Воздействие громких звуков\n• Стресс и переутомление\n• Некоторые лекарства\n• Проблемы с сосудами\n\n**Что делать:**\n• Обратитесь к врачу для диагностики\n• Избегайте громких звуков\n• Снижайте стресс\n• Проверяйте принимаемые лекарства\n\nНе игнорируйте постоянный звон - это может быть сигналом проблемы!",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/tinnitus-pochemu-ya-slyshu-zvon-v-ushakh",
                    },
                    {
                        "title": "Как понять, что снижен слух?",
                        "description": "Признаки снижения слуха",
                        "bot_message": "Вот подсказки, на какие сигналы стоит обратить внимание 🧐\n\nНо не переживай: это только для ориентира. Если будут сомнения — лучше обратиться к специалисту.",
                        "content": "👂 **Признаки снижения слуха**\n\nВажно вовремя заметить признаки проблем со слухом:\n\n**В повседневной жизни:**\n• Просите повторить сказанное\n• Увеличиваете громкость ТВ/радио\n• Плохо слышите в шумных местах\n• Не слышите дверной звонок\n• Громко разговариваете сами\n\n**Симптомы:**\n• Звон или шум в ушах\n• Чувство заложенности\n• Боль или давление в ушах\n• Головокружение\n\n**Что делать:**\n• Пройдите тест на слух\n• Обратитесь к специалисту\n• Не откладывайте диагностику\n\nРаннее выявление помогает сохранить слух!",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/kak-uznat-chto-snizhen-slukh",
                    },
                ]

                for subitem_data in symptoms_subitems:
                    menu_item = MenuItem(
                        title=subitem_data["title"],
                        description=subitem_data["description"],
                        bot_message=subitem_data["bot_message"],
                        web_app_url=subitem_data.get("web_app_url"),
                        parent_id=symptoms_item.id,
                        is_active=True,
                        access_level=AccessLevel.FREE,
                    )
                    session.add(menu_item)
                    await session.flush()

                    content = ContentFile(
                        menu_item_id=menu_item.id,
                        content_type=ContentType.TEXT,
                        content_text=subitem_data["content"],
                        is_primary=True,
                        sort_order=1,
                    )
                    session.add(content)

        await session.commit()

        # Создаем под-подразделы для "Хочу узнать про заботу о слухе"
        if "Хочу узнать про заботу о слухе" in created_items:
            care_item = created_items["Хочу узнать про заботу о слухе"]

            care_subitems = [
                {
                    "title": "Как сохранить слух",
                    "description": "Советы по сохранению слуха",
                    "bot_message": "Важно, чтобы людям с особенностями слуха было комфортно 💙 \n\nВот несколько советов и материалов, которые помогут адаптироваться и поддерживать качество жизни.",
                    "content": "🛡️ **Как сохранить слух**\n\nПодборка материалов о профилактике и поддержке слуха.",
                },
                {
                    "title": "Жизнь с особенностями слуха",
                    "description": "Материалы о жизни с особенностями слуха",
                    "bot_message": "Мы собрали для тебя полезные статьи и подкасты о том, как заботиться о слухе💙",
                    "content": "💙 **Жизнь с особенностями слуха**\n\nПолезные материалы и подкасты.",
                },
            ]

            created_care_items = {}
            for subitem_data in care_subitems:
                menu_item = MenuItem(
                    title=subitem_data["title"],
                    description=subitem_data["description"],
                    bot_message=subitem_data["bot_message"],
                    parent_id=care_item.id,
                    is_active=True,
                    access_level=AccessLevel.FREE,
                )
                session.add(menu_item)
                await session.flush()

                content = ContentFile(
                    menu_item_id=menu_item.id,
                    content_type=ContentType.TEXT,
                    content_text=subitem_data["content"],
                    is_primary=True,
                    sort_order=1,
                )
                session.add(content)

                created_care_items[subitem_data["title"]] = menu_item

            await session.commit()

            # Под-под-подразделы для "Как сохранить слух"
            if "Как сохранить слух" in created_care_items:
                how_to_save_item = created_care_items["Как сохранить слух"]

                how_to_save_links = [
                    {
                        "title": "Как потеря слуха влияет на здоровье",
                        "description": "Статья о влиянии потери слуха",
                        "bot_message": care_subitems[0]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/what-happens/",
                    },
                    {
                        "title": "10 мифов о потере слуха",
                        "description": "Статья о мифах",
                        "bot_message": care_subitems[0]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/10-mifov-o-potere-slukha",
                    },
                    {
                        "title": "Как общаться со слабослышащими людьми",
                        "description": "Рекомендации по общению",
                        "bot_message": care_subitems[0]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/kak-obshchatsya-so-slaboslyshashchimi-lyudmi",
                    },
                    {
                        "title": "6 плюсов потери слуха",
                        "description": "Позитивные аспекты",
                        "bot_message": care_subitems[0]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/plyusy-poteri-slukha-6-punktov-o-kotorykh-vy-vozmozhno-dazhe-ne-zadumyvalis",
                    },
                ]

                for link in how_to_save_links:
                    menu_item = MenuItem(
                        title=link["title"],
                        description=link["description"],
                        bot_message=link["bot_message"],
                        web_app_url=link.get("web_app_url"),
                        parent_id=how_to_save_item.id,
                        is_active=True,
                        access_level=AccessLevel.FREE,
                    )
                    session.add(menu_item)
                    await session.flush()

                    content = ContentFile(
                        menu_item_id=menu_item.id,
                        content_type=ContentType.TEXT,
                        content_text=link["content"],
                        is_primary=True,
                        sort_order=1,
                    )
                    session.add(content)

            # Под-под-подразделы для "Жизнь с особенностями слуха"
            if "Жизнь с особенностями слуха" in created_care_items:
                life_with_hearing_item = created_care_items["Жизнь с особенностями слуха"]

                life_with_hearing_links = [
                    {
                        "title": "10 советов, как сохранить слух",
                        "description": "Практические советы",
                        "bot_message": care_subitems[1]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/10-sovetov-kak-sokhranit-sluh",
                    },
                    {
                        "title": "Как заметить нарушения слуха и что делать",
                        "description": "Памятка и чек-лист",
                        "bot_message": care_subitems[1]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/skachat/ya-tebya-uslyshal-kak-zametit-narusheniya-slukha-i-chto-delat",
                    },
                    {
                        "title": "Подкаст «Влияние громкой музыки на слух»",
                        "description": "Подкаст о громкой музыке",
                        "bot_message": care_subitems[1]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/vypusk-podkasta-vliyanie-gromkoy-muzyki-na-slukh",
                    },
                    {
                        "title": "Подкаст «Кто сказал, что слух - навсегда?»",
                        "description": "Подкаст о слухе",
                        "bot_message": care_subitems[1]["bot_message"],
                        "content": "Материал на сайте ihearyou.ru",
                        "web_app_url": "https://www.ihearyou.ru/materials/articles/vypusk-podkasta-kto-skazal-chto-slukh-navsegda",
                    },
                ]

                for link in life_with_hearing_links:
                    menu_item = MenuItem(
                        title=link["title"],
                        description=link["description"],
                        bot_message=link["bot_message"],
                        web_app_url=link.get("web_app_url"),
                        parent_id=life_with_hearing_item.id,
                        is_active=True,
                        access_level=AccessLevel.FREE,
                    )
                    session.add(menu_item)
                    await session.flush()

                    content = ContentFile(
                        menu_item_id=menu_item.id,
                        content_type=ContentType.TEXT,
                        content_text=link["content"],
                        is_primary=True,
                        sort_order=1,
                    )
                    session.add(content)

            await session.commit()

    async def _create_subitems(self, session, parent_id: int, subitems: List[Dict[str, Any]]):
        """Создать подразделы для родительского пункта меню."""
        for subitem_data in subitems:
            # Создаем пункт меню
            menu_item = MenuItem(
                title=subitem_data["title"],
                description=subitem_data["description"],
                bot_message=subitem_data["bot_message"],
                web_app_url=subitem_data.get("web_app_url"),
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
