import os
from typing import Optional

import kb
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from api_client import APIClient
from dict import DICT as dict
from dict import DICT_KB as dict_kb
from handlers_navigation import edit_message, navigation_states
from states import NavigationState, States

router = Router()

bot = Bot(token=os.getenv("BOT_TOKEN"))
 

@router.callback_query(F.data == "go_back_cd")
async def handle_go_back_inline(callback: CallbackQuery, state: FSMContext):
    """Обработчик для inline кнопки 'Назад'"""
    # Записываем активность - навигация назад
    async with APIClient() as api:
        await api.record_activity(
            telegram_user_id=callback.from_user.id,
            menu_item_id=1,  # Навигация
            activity_type="navigation"
        )
    
    user_id = callback.from_user.id

    if user_id not in navigation_states or len(navigation_states[user_id].history) <= 1:
        # Если нет истории навигации, возвращаем в главное меню
        # Получаем главное меню из API
        async with APIClient() as api:
            menu_items = await api.get_menu_items(
                telegram_user_id=callback.from_user.id,
                parent_id=None
            )
        
        if menu_items:
            keyboard = kb.create_dynamic_keyboard(menu_items, parent_id=None)
            await edit_message(
                callback,
                dict["hello"].format(name=callback.from_user.first_name),
                keyboard
            )
        else:
            await edit_message(
                callback,
                "К сожалению, сервис временно недоступен. Попробуйте позже.",
                kb.rate_keyboard
            )
        return

    nav_state = navigation_states[user_id]
    previous_state = nav_state.go_back()

    if previous_state:
        # Если возвращаемся на экран оценки — восстановим FSM
        meta = previous_state.get('meta') or {}
        if meta.get('screen') == 'rating':
            await state.set_state(States.waiting_for_article_rating)
            if 'article_name' in meta:
                await state.update_data(article_name=meta['article_name'])
        await edit_message(
            callback,
            previous_state['message_text'],
            previous_state['reply_markup'],
            add_to_history=False,
            meta=meta,
        )
    else:
        # Если не удалось получить предыдущее состояние, возвращаем в главное меню
        # Получаем главное меню из API
        async with APIClient() as api:
            menu_items = await api.get_menu_items(
                telegram_user_id=callback.from_user.id,
                parent_id=None
            )
        
        if menu_items:
            keyboard = kb.create_dynamic_keyboard(menu_items, parent_id=None)
            await edit_message(
                callback,
                dict["hello"].format(name=callback.from_user.first_name),
                keyboard
            )
        else:
            await edit_message(
                callback,
                "К сожалению, сервис временно недоступен. Попробуйте позже.",
                kb.rate_keyboard
            )


# Обработчик для кнопки "Задать вопрос" (inline)
@router.callback_query(F.data == "ask_question_cd")
async def handle_ask_question_inline(callback: CallbackQuery, state: FSMContext):
    """Открыть форму ввода вопроса."""
    await state.clear()
    await state.set_state(States.waiting_for_user_question)

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    nav_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=dict_kb["go_back"], callback_data="go_back_cd"),
            InlineKeyboardButton(text=dict_kb["go_home"], callback_data="main_cd"),
        ]
    ])

    await edit_message(
        callback,
        "Тут ты сможешь задать интересующий вопрос нам, а мы постараемся ответить как можно быстрее!",
        nav_keyboard,
    )


@router.message(States.waiting_for_user_question)
async def handle_user_question_text(message: Message, state: FSMContext):
    """Принимаем текст вопроса, сохраняем в БД, подтверждаем пользователю."""
    question_text = message.text.strip()
    if not question_text:
        await message.answer("Пожалуйста, напишите ваш вопрос текстом.")
        return

    # Сохраняем вопрос
    async with APIClient() as api:
        await api.create_user_question(
            telegram_user_id=message.from_user.id,
            question=question_text,
        )

    await state.clear()

    await message.answer(
        "Спасибо! Ваш вопрос отправлен. Мы уведомим вас, когда будет готов ответ.")

# Обработчик для кнопки "Написать письмо" (inline)
@router.callback_query(F.data == "write_letter_cd")
async def handle_write_letter_inline(callback: CallbackQuery):
    """Обработчик для inline кнопки 'Написать письмо' (заглушка)"""
    # Записываем активность
    async with APIClient() as api:
        await api.record_activity(
            telegram_user_id=callback.from_user.id,
            menu_item_id=2,  # Используем существующий ID пункта меню
            activity_type="letter_click"
        )
    
    # Создаем навигационную клавиатуру с кнопками "Назад" и "Главное меню"
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    nav_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=dict_kb["go_back"], callback_data="go_back_cd"),
            InlineKeyboardButton(text=dict_kb["ask_question"], callback_data="ask_question_cd"),
        ],
        [InlineKeyboardButton(text=dict_kb["go_home"], callback_data="main_cd")]
    ])
    
    await edit_message(
        callback,
        dict["write_letter_placeholder"],
        nav_keyboard
    )

@router.callback_query(F.data.startswith("rate_item_"))
async def handle_open_rate_for_item(callback: CallbackQuery, state: FSMContext):
    """Открыть форму оценки конкретного материала (привязан к item_id)."""
    # Извлекаем ID пункта из callback
    try:
        item_id = int(callback.data.replace("rate_item_", "").replace("_cd", ""))
    except Exception:
        return

    # Сохраняем состояние ожидания оценки и item_id
    await state.set_state(States.waiting_for_article_rating)
    await state.update_data(article_name=f"Материал #{item_id}")
    await state.update_data(menu_item_id=item_id)

    await edit_message(
        callback,
        dict["rate"],
        kb.rate_keyboard,
        meta={"screen": "rating", "menu_item_id": item_id},
    )


@router.callback_query(F.data.in_({"rate_1_cd", "rate_2_cd", "rate_3_cd", "rate_4_cd", "rate_5_cd"}), States.waiting_for_article_rating)
async def handle_article_rating(callback: CallbackQuery, state: FSMContext):
    """Универсальный обработчик для всех оценок статей"""

    # Получаем данные из состояния
    data = await state.get_data()
    article_name = data.get("article_name")
    menu_item_id = data.get("menu_item_id")

    if not menu_item_id:
        # Создаем простую навигационную клавиатуру
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        nav_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=dict_kb["go_back"], callback_data="go_back_cd"),
                InlineKeyboardButton(text=dict_kb["ask_question"], callback_data="ask_question_cd"),
            ],
            [InlineKeyboardButton(text=dict_kb["go_home"], callback_data="main_cd")]
        ])
        await edit_message(callback, "Произошла ошибка. Попробуйте еще раз.", nav_keyboard)
        await state.clear()
        return

    # Определяем оценку по callback_data
    rating_map = {
        "rate_1_cd": 1,
        "rate_2_cd": 2,
        "rate_3_cd": 3,
        "rate_4_cd": 4,
        "rate_5_cd": 5,
    }
    rating = rating_map.get(callback.data, 0)

    # Сохраняем оценку через API
    async with APIClient() as api:
        # Записываем саму оценку
        await api.rate_material(
            telegram_user_id=callback.from_user.id,
            menu_item_id=menu_item_id,
            rating=rating
        )

    # Выходим из состояния
    await state.clear()

    # Удаляем форму оценки: показываем предыдущий экран из истории
    user_id = callback.from_user.id
    user_state = navigation_states.get(user_id)
    if user_state and len(user_state.history) >= 2:
        # Удаляем последний (форма оценки)
        user_state.history.pop()
        previous_state = user_state.history[-1]
        await edit_message(
            callback,
            previous_state['message_text'],
            previous_state['reply_markup'],
            add_to_history=False,
        )
        # И отправляем короткое уведомление
        await callback.answer(dict["get_rate"].format(article_name=article_name or "Материал", rating=rating), show_alert=False)
    else:
        # Если истории нет — просто сообщение с навигацией
        from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
        nav_keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text=dict_kb["go_back"], callback_data="go_back_cd"),
                InlineKeyboardButton(text=dict_kb["ask_question"], callback_data="ask_question_cd"),
            ],
            [InlineKeyboardButton(text=dict_kb["go_home"], callback_data="main_cd")]
        ])
        await edit_message(callback, dict["get_rate"].format(article_name=article_name or "Материал", rating=rating), nav_keyboard)


#------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    # Создаем пользователя через API
    async with APIClient() as api:
        await api.create_telegram_user(
            telegram_id=message.from_user.id,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            username=message.from_user.username
        )
        
        # Записываем активность - команда /start
        await api.record_activity(
            telegram_user_id=message.from_user.id,
            menu_item_id=1,  # Главное меню
            activity_type="start_command"
        )

    # Получаем главное меню из API
    async with APIClient() as api:
        menu_items = await api.get_menu_items(
            telegram_user_id=message.from_user.id,
            parent_id=None
        )
    
    if menu_items:
        keyboard = kb.create_dynamic_keyboard(menu_items, parent_id=None)
        
        # Инициализируем навигацию для пользователя
        navigation_states[message.from_user.id] = NavigationState()
        navigation_states[message.from_user.id].add_state(
            dict["hello"].format(name=message.from_user.first_name),
            keyboard
        )

        # Отправляем основное сообщение с inline клавиатурой
        await message.answer(
            dict["hello"].format(name=message.from_user.first_name),
            reply_markup=keyboard
        )
    else:
        # Fallback если API недоступен
        await message.answer(
            "Привет! К сожалению, сервис временно недоступен. Попробуйте позже.",
            reply_markup=kb.rate_keyboard  # Простая клавиатура как fallback
        )


@router.callback_query(F.data == "main_cd")
async def handle_main_cd(callback: CallbackQuery):
    # Записываем активность - возврат в главное меню
    async with APIClient() as api:
        await api.record_activity(
            telegram_user_id=callback.from_user.id,
            menu_item_id=1,  # Главное меню
            activity_type="navigation"
        )
        
        # Получаем главное меню из API
        menu_items = await api.get_menu_items(
            telegram_user_id=callback.from_user.id,
            parent_id=None
        )
    
    if menu_items:
        keyboard = kb.create_dynamic_keyboard(menu_items, parent_id=None)
        await edit_message(
            callback,
            dict["hello"].format(name=callback.from_user.first_name),
            keyboard
        )
    else:
        await edit_message(
            callback,
            "К сожалению, сервис временно недоступен. Попробуйте позже.",
            kb.rate_keyboard
        )

# Универсальный обработчик для пунктов меню
@router.callback_query(F.data.startswith("menu_item_"))
async def handle_menu_item(callback: CallbackQuery):
    """Обработчик для динамических пунктов меню"""
    # Извлекаем ID пункта меню из callback_data
    menu_item_id = int(callback.data.replace("menu_item_", "").replace("_cd", ""))
    
    # Записываем активность - навигация по меню
    async with APIClient() as api:
        await api.record_activity(
            telegram_user_id=callback.from_user.id,
            menu_item_id=menu_item_id,
            activity_type="navigation"
        )
        
        # Сначала проверяем наличие дочерних элементов
        submenu_items = await api.get_menu_items(
            telegram_user_id=callback.from_user.id,
            parent_id=menu_item_id
        )
    
    if submenu_items:
        # Если есть дочерние элементы, показываем их
        # Записываем активность - вход в раздел
        async with APIClient() as api:
            await api.record_activity(
                telegram_user_id=callback.from_user.id,
                menu_item_id=menu_item_id,
                activity_type="section_enter"
            )

        # Получаем сообщение бота из самого пункта меню
        async with APIClient() as api:
            parent_content = await api.get_menu_content(
                menu_item_id=menu_item_id,
                telegram_user_id=callback.from_user.id
            )

        # Используем сообщение из самого пункта меню
        bot_message = parent_content.get("bot_message") if parent_content else "Выберите раздел:"

        keyboard = kb.create_dynamic_keyboard(submenu_items, parent_id=menu_item_id)
        await edit_message(callback, bot_message, keyboard)
    else:
        # Если дочерних элементов нет, показываем контент
        async with APIClient() as api:
            content = await api.get_menu_content(
                menu_item_id=menu_item_id,
                telegram_user_id=callback.from_user.id
            )
        
        if content:
            # Записываем активность - открытие материала
            async with APIClient() as api:
                await api.record_activity(
                    telegram_user_id=callback.from_user.id,
                    menu_item_id=menu_item_id,
                    activity_type="material_open"
                )
            
            # Если есть контент, показываем его
            message_text = content.get("bot_message", "Выберите раздел:")
            
            # Если есть контентные файлы, добавляем их текст к сообщению
            content_files = content.get("content_files", [])
            if content_files:
                primary_content = next((cf for cf in content_files if cf.get("is_primary")), content_files[0])
                if primary_content and primary_content.get("content_text"):
                    message_text += "\n\n" + primary_content["content_text"]
            
            keyboard = kb.create_content_keyboard(content)
            await edit_message(callback, message_text, keyboard)
        else:
            await edit_message(
                callback,
                "Контент временно недоступен. Попробуйте позже.",
                kb.rate_keyboard
            )


@router.callback_query(F.data == "rate_material_cd")
async def handle_rate_material(callback: CallbackQuery, state: FSMContext):
    """Обработчик для оценки материала"""
    # Получаем информацию о текущем контенте из состояния навигации
    user_state = navigation_states.get(callback.from_user.id)
    if not user_state or not user_state.history:
        await edit_message(
            callback,
            "Ошибка: не удалось определить материал для оценки.",
            kb.rate_keyboard
        )
        return
    
    # Сохраняем информацию о материале для оценки
    await state.set_state(States.waiting_for_article_rating)
    await state.update_data(article_name="Материал")
    
    await edit_message(
        callback,
        dict["rate"],
        kb.rate_keyboard
    )
