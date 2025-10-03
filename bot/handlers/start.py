"""Обработчик команды /start и главного меню."""

import logging

from aiogram import F, Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from ..config import settings
from ..services.menu_service import MenuService
from ..utils.api_client import APIClientError
from ..utils.keyboards import create_main_menu_keyboard, create_menu_keyboard


logger = logging.getLogger(__name__)


# Состояния FSM
class UserStates(StatesGroup):
    """Состояния пользователя в FSM."""

    main_menu = State()  # Главное меню
    selected_path = State()  # Выбранный путь (ребенок/взрослый)
    menu_navigation = State()  # Навигация по меню
    content_view = State()  # Просмотр контента
    search_waiting = State()  # Ожидание поискового запроса
    question_input = State()  # Ввод вопроса
    rating_waiting = State()  # Ожидание оценки


# Создаем роутер
router = Router()
menu_service = MenuService()


@router.message(CommandStart())
@router.callback_query(F.data == "home")
async def start_handler(message_or_callback: types.Message | types.CallbackQuery, state: FSMContext):
    """Обработчик команды /start и возврата в главное меню."""
    try:
        # Очищаем состояние FSM
        await state.clear()
        await state.set_state(UserStates.main_menu)

        # Создаем клавиатуру главного меню
        keyboard = create_main_menu_keyboard()

        welcome_text = (
            f"{settings.welcome_message}\n\n"
            f"Мы понимаем, как важно для вас найти правильные ответы на вопросы о слухе. "
            f"Выберите направление, которое вас интересует, и мы поможем найти нужную информацию."
        )

        if isinstance(message_or_callback, types.CallbackQuery):
            await message_or_callback.message.edit_text(
                text=welcome_text,
                reply_markup=keyboard,
                parse_mode=settings.parse_mode,
                disable_web_page_preview=settings.disable_web_page_preview,
            )
            await message_or_callback.answer()
        else:
            await message_or_callback.answer(
                text=welcome_text,
                reply_markup=keyboard,
                parse_mode=settings.parse_mode,
                disable_web_page_preview=settings.disable_web_page_preview,
            )

    except Exception as e:
        logger.error(f"Error in start handler: {e}")

        error_text = settings.error_message

        if isinstance(message_or_callback, types.CallbackQuery):
            try:
                await message_or_callback.message.edit_text(error_text)
                await message_or_callback.answer("Произошла ошибка", show_alert=True)
            except Exception:
                pass
        else:
            try:
                await message_or_callback.answer(error_text)
            except Exception:
                pass


@router.callback_query(F.data.in_(["path_child", "path_adult"]))
async def select_path_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик выбора пути (ребенок/взрослый)."""
    try:
        # Получаем telegram_user_id из события
        telegram_user_id = callback.from_user.id

        path_type = callback.data
        path_text = "ребенка" if path_type == "path_child" else "своего"

        # Сохраняем выбранный путь
        await state.set_state(UserStates.selected_path)
        await state.update_data(path_type=path_type)

        # Загружаем первые пункты меню (главные разделы)
        menu_items = await menu_service.get_menu_items(telegram_user_id=telegram_user_id, parent_id=None)

        if not menu_items:
            await callback.message.edit_text(
                "😔 К сожалению, в данный момент материалы недоступны. "
                "Попробуйте позже или обратитесь к администратору.",
                parse_mode=settings.parse_mode,
            )
            await callback.answer("Материалы недоступны", show_alert=True)
            return

        # Создаем клавиатуру с пунктами меню
        keyboard = create_menu_keyboard(menu_items)

        message_text = (
            f"✅ Вы выбрали направление: {path_text} слухе\n\n" f"🔍 Теперь выберите раздел, который вас интересует:"
        )

        await callback.message.edit_text(
            text=message_text,
            reply_markup=keyboard,
            parse_mode=settings.parse_mode,
            disable_web_page_preview=settings.disable_web_page_preview,
        )

        await callback.answer()

    except APIClientError as e:
        logger.error(f"API error in select_path_handler: {e}")
        await callback.answer("Ошибка загрузки меню", show_alert=True)

    except Exception as e:
        logger.error(f"Error in select_path_handler: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data == "back")
async def back_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки 'Назад'."""
    try:
        # Получаем telegram_user_id из события
        telegram_user_id = callback.from_user.id

        current_state = await state.get_state()
        state_data = await state.get_data()

        if current_state == UserStates.selected_path:
            # Возвращаемся к выбору пути
            await callback.message.edit_text(
                text=settings.welcome_message,
                reply_markup=create_main_menu_keyboard(),
                parse_mode=settings.parse_mode,
                disable_web_page_preview=settings.disable_web_page_preview,
            )
            await state.set_state(UserStates.main_menu)

        elif current_state == UserStates.menu_navigation:
            # Возвращаемся к предыдущему уровню меню
            parent_id = state_data.get("parent_id")

            if parent_id is None:
                # Возвращаемся к выбору пути
                await callback.message.edit_text(
                    text=settings.welcome_message,
                    reply_markup=create_main_menu_keyboard(),
                    parse_mode=settings.parse_mode,
                    disable_web_page_preview=settings.disable_web_page_preview,
                )
                await state.set_state(UserStates.main_menu)
            else:
                # Загружаем родительское меню
                menu_items = await menu_service.get_menu_items(telegram_user_id=telegram_user_id, parent_id=parent_id)

                if menu_items:
                    keyboard = create_menu_keyboard(menu_items)
                    await callback.message.edit_text(
                        text="🔍 Выберите раздел:",
                        reply_markup=keyboard,
                        parse_mode=settings.parse_mode,
                        disable_web_page_preview=settings.disable_web_page_preview,
                    )
                else:
                    await callback.message.edit_text(
                        text="❌ Нет доступных пунктов меню",
                        reply_markup=create_main_menu_keyboard(),
                        parse_mode=settings.parse_mode,
                    )
                    await state.set_state(UserStates.main_menu)

        await callback.answer()

    except Exception as e:
        logger.error(f"Error in back_handler: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)
