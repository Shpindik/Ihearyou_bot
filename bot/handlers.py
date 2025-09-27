import os

import kb
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from db import save_article_rating, save_user_data
from dict import DICT as dict
from dict import DICT_KB as dict_kb
from handlers_navigation import edit_message, navigation_states
from states import NavigationState, States

router = Router()

bot = Bot(token=os.getenv("BOT_TOKEN"))
 

@router.callback_query(F.data == "go_back_cd")
async def handle_go_back_inline(callback: CallbackQuery, state: FSMContext):
    """Обработчик для inline кнопки 'Назад'"""
    user_id = callback.from_user.id

    if user_id not in navigation_states or len(navigation_states[user_id].history) <= 1:
        # Если нет истории навигации, возвращаем в главное меню
        await edit_message(
            callback,
            dict["hello"].format(name=callback.from_user.first_name),
            kb.main_keyboard
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
        await edit_message(
            callback,
            dict["hello"].format(name=callback.from_user.first_name),
            kb.main_keyboard
        )


# Обработчик для кнопки "Задать вопрос" (inline)
@router.callback_query(F.data == "ask_question_cd")
async def handle_ask_question_inline(callback: CallbackQuery):
    """Обработчик для inline кнопки 'Задать вопрос' (заглушка)"""
    await edit_message(
        callback,
        "❓ Функция 'Задать вопрос' пока в разработке.\n\n"
        "Скоро здесь будет возможность связаться с нашими специалистами!",
        kb.main_keyboard
    )

@router.callback_query(F.data.in_({"rate_1_cd", "rate_2_cd", "rate_3_cd", "rate_4_cd", "rate_5_cd"}), States.waiting_for_article_rating)
async def handle_article_rating(callback: CallbackQuery, state: FSMContext):
    """Универсальный обработчик для всех оценок статей"""

    # Получаем данные из состояния
    data = await state.get_data()
    article_name = data.get("article_name")

    if not article_name:
        await edit_message(callback, "Произошла ошибка. Попробуйте еще раз.", kb.go_home_keyboard)
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

    # Сохраняем оценку в БД
    await save_article_rating(
        user_id=callback.from_user.id,
        article_name=article_name,
        rating=rating,
    )

    # Выходим из состояния
    await state.clear()

    # Показываем сообщение об успешном сохранении
    message_text = dict["get_rate"].format(article_name=article_name, rating=rating)
    await edit_message(callback, message_text, kb.go_home_keyboard)


#------------------------------------------------------------------------------------------------

#------------------------------------------------------------------------------------------------

@router.message(F.text == "/start")
async def cmd_start(message: Message):
    await save_user_data(message.from_user.id, message.from_user.username, message.from_user.full_name)

    # Инициализируем навигацию для пользователя
    navigation_states[message.from_user.id] = NavigationState()
    navigation_states[message.from_user.id].add_state(
        dict["hello"].format(name=message.from_user.first_name),
        kb.main_keyboard
    )

    # Отправляем основное сообщение с inline клавиатурой
    await message.answer(
        dict["hello"].format(name=message.from_user.first_name),
        reply_markup=kb.main_keyboard
    )


@router.callback_query(F.data == "main_cd")
async def handle_main_cd(callback: CallbackQuery):
    await edit_message(
        callback,
        dict["hello"].format(name=callback.from_user.first_name),
        kb.main_keyboard
    )



@router.callback_query(F.data == "button_1_cd")
async def handle_button_1_cd(callback: CallbackQuery):
    await edit_message(callback, dict["good_choise"], kb.go_home_keyboard)


@router.callback_query(F.data == "button_2_cd")
async def handle_button_2_cd(callback: CallbackQuery):
    await edit_message(callback, dict["self_hearing_intro"], kb.self_hearing_keyboard)


@router.callback_query(F.data == "button_3_cd")
async def handle_button_3_cd(callback: CallbackQuery):
    await edit_message(callback, dict["check_hearing_intro"], kb.check_hearing_keyboard)


@router.callback_query(F.data == "button_6_cd")
async def handle_button_6_cd(callback: CallbackQuery):
    await edit_message(callback, dict["check_hearing_links_intro"], kb.check_hearing_links_keyboard)


@router.callback_query(F.data == "select_article_for_rating_cd")
async def handle_select_article_for_rating(callback: CallbackQuery):
    """Обработчик для выбора статьи для оценки"""
    await edit_message(callback, dict["select_rate"], kb.select_article_rating_keyboard_1)


@router.callback_query(F.data == "rate_test_article_cd")
async def handle_rate_test_article(callback: CallbackQuery, state: FSMContext):
    """Обработчик для оценки онлайн-теста"""
    message_text = dict["chose_rate"].format(article_name=dict_kb["check_hearing_test"], rate=dict["rate"])
    await edit_message(
        callback,
        message_text,
        kb.rate_keyboard,
        meta={"screen": "rating", "article_name": dict_kb["check_hearing_test"]},
    )

    await state.set_state(States.waiting_for_article_rating)
    await state.update_data(article_name=dict_kb["check_hearing_test"])


@router.callback_query(F.data == "rate_article_cd")
async def handle_rate_article(callback: CallbackQuery, state: FSMContext):
    """Обработчик для оценки статьи «8 причин»"""
    message_text = dict["chose_rate"].format(article_name=dict_kb["check_hearing_article"], rate=dict["rate"])
    await edit_message(
        callback,
        message_text,
        kb.rate_keyboard,
        meta={"screen": "rating", "article_name": dict_kb["check_hearing_article"]},
    )

    await state.set_state(States.waiting_for_article_rating)
    await state.update_data(article_name=dict_kb["check_hearing_article"])
