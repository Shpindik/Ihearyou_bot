"""Обработчики оценки материалов."""

import asyncio
import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from ..config import settings
from ..services.rating_service import RatingService
from ..services.user_activity_service import UserActivityService
from ..utils.keyboards import create_back_menu_keyboard, create_rating_keyboard
from .start import UserStates


logger = logging.getLogger(__name__)

router = Router()
rating_service = RatingService()
activity_service = UserActivityService()


@router.callback_query(F.data.startswith("content_rating_"))
async def rating_request_handler(callback: types.CallbackQuery, state: FSMContext, telegram_user_id: int):
    """Обработчик запроса оценки материала."""
    try:
        # Извлекаем ID пункта меню
        menu_item_id = int(callback.data.split("_")[2])

        # Сохраняем контекст для оценки
        await state.set_state(UserStates.rating_waiting)
        await state.update_data(rating_menu_id=menu_item_id)

        # Запрашиваем оценку материала
        menu_item_info = await rating_service.get_menu_item_info(menu_item_id, telegram_user_id)

        if not menu_item_info:
            await callback.answer("Материал не найден", show_alert=True)
            return

        title = menu_item_info.get("title", "Мaterial")

        message_text = (
            f"⭐ Оцените полезность материала «{title}»:\n\n"
            f"Выберите оценку от 1 до 5 звезд:\n"
            f"1 ⭐ - Не полезен\n"
            f"2 ⭐⭐ - Мало полезен\n"
            f"3 ⭐⭐⭐ - Умеренно полезен\n"
            f"4 ⭐⭐⭐⭐ - Очень полезен\n"
            f"5 ⭐⭐⭐⭐⭐ - Исключительно полезен"
        )

        keyboard = create_rating_keyboard()

        # Добавляем кнопку "Отмена"
        keyboard = add_cancel_button_to_keyboard(keyboard, f"content_menu_{menu_item_id}")

        await callback.message.edit_text(text=message_text, reply_markup=keyboard, parse_mode=settings.parse_mode)

        await callback.answer()

    except ValueError:
        await callback.answer("Неверный формат данных", show_alert=True)
    except Exception as e:
        logger.error(f"Error in rating_request_handler: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data.startswith("rate_"))
async def rating_submit_handler(callback: types.CallbackQuery, state: FSMContext, telegram_user_id: int):
    """Обработчик отправки оценки материала."""
    try:
        current_state = await state.get_state()

        if current_state != UserStates.rating_waiting:
            await callback.answer("Ошибка контекста оценки", show_alert=True)
            return

        # Извлекаем рейтинг
        rating = int(callback.data.split("_")[1])

        if not (1 <= rating <= 5):
            await callback.answer("Неверная оценка", show_alert=True)
            return

        # Получаем данные из FSM
        state_data = await state.get_data()
        menu_item_id = state_data.get("rating_menu_id")

        if not menu_item_id:
            await callback.answer("Ошибка контекста", show_alert=True)
            return

        # Отправляем оценку в API
        success = await rating_service.submit_rating(
            telegram_user_id=telegram_user_id, menu_item_id=menu_item_id, rating=rating
        )

        if success:
            # Логируем активность
            await activity_service.log_rating(telegram_user_id, menu_item_id, rating)

            # Показываем подтверждение
            rating_words = {
                1: "Не полезен",
                2: "Мало полезен",
                3: "Умеренно полезен",
                4: "Очень полезен",
                5: "Исключительно полезен",
            }

            confirmation_text = (
                f"✅ Спасибо за вашу оценку!\n\n"
                f"Материал оценен как: {rating_words[rating]}\n\n"
                f"Ваше мнение поможет нам улучшить качество материалов."
            )

            await callback.message.edit_text(text=confirmation_text, parse_mode=settings.parse_mode)

            # Возвращаемся к просмотру контента или меню
            await asyncio.sleep(2)  # Даем время прочитать подтверждение

            # Создаем клавиатуру возврата к контенту
            from ..utils.keyboards import create_content_actions_keyboard

            keyboard = create_content_actions_keyboard(menu_item_id)

            await callback.message.edit_text(
                text=f"📄 Материал: {state_data.get('content_title', 'Описание материала')}",
                reply_markup=keyboard,
                parse_mode=settings.parse_mode,
            )

            await state.set_state(UserStates.content_view)

        else:
            await callback.message.edit_text(
                text="😔 Произошла ошибка при сохранении оценки. Попробуйте позже.",
                reply_markup=create_back_menu_keyboard(),
                parse_mode=settings.parse_mode,
            )

        await callback.answer()

    except ValueError:
        await callback.answer("Неверная оценка", show_alert=True)
    except Exception as e:
        logger.error(f"Error in rating_submit_handler: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


def add_cancel_button_to_keyboard(keyboard, cancel_callback: str):
    """Добавляет кнопку отмены к существующей клавиатуре."""
    # Создаем копию существующих кнопок
    keyboard_rows = keyboard.inline_keyboard.copy()

    # Добавляем кнопку отмены
    cancel_row = [types.InlineKeyboardButton(text="❌ Отмена", callback_data=cancel_callback)]

    keyboard_rows.append(cancel_row)

    return types.InlineKeyboardMarkup(inline_keyboard=keyboard_rows)
