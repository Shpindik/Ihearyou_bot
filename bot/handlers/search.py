"""Обработчик поиска по материалам."""

import logging
from typing import Any, Dict, List

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from ..config import settings
from ..services.menu_service import MenuService
from ..services.user_activity_service import UserActivityService
from ..utils.keyboards import (
    create_back_menu_keyboard,
    create_search_pagination_keyboard,
    create_search_results_keyboard,
)
from .start import UserStates


logger = logging.getLogger(__name__)

router = Router()
menu_service = MenuService()
activity_service = UserActivityService()


@router.callback_query(F.data == "search")
@router.callback_query(F.data.startswith("search_page_"))
async def search_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик кнопки поиска."""
    try:
        # Получаем telegram_user_id из события
        telegram_user_id = callback.from_user.id

        # Если это пагинация поиска
        if callback.data.startswith("search_page_"):
            page = int(callback.data.split("_")[-1])
            state_data = await state.get_data()
            search_query = state_data.get("search_query")

            if not search_query:
                await callback.answer("Результаты поиска устарели", show_alert=True)
                return
        else:
            # Новый поиск - запрашиваем запрос
            await callback.message.edit_text(
                text="🔍 Введите поисковый запрос:\n\n" "Например: слуховые аппараты, диагностика, развитие речи",
                parse_mode=settings.parse_mode,
            )

            await state.set_state(UserStates.search_waiting)
            await callback.answer()
            return

        # Выполняем поиск
        await perform_search(callback, telegram_user_id, search_query, page)

    except Exception as e:
        logger.error(f"Error in search_handler: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.message(F.text, lambda message: len(message.text) >= 2)
async def search_text_handler(message: types.Message, state: FSMContext):
    """Обработчик текстового поискового запроса."""
    try:
        # Получаем telegram_user_id из события
        telegram_user_id = message.from_user.id

        current_state = await state.get_state()

        if current_state != UserStates.search_waiting:
            # Если пользователь не ожидает поиска, игнорируем сообщение
            return

        search_query = message.text.strip()

        if len(search_query) < 2:
            await message.answer("Поисковый запрос должен содержать минимум 2 символа")
            return

        # Сохраняем запрос поиска
        await state.update_data(search_query=search_query)

        # Выполняем поиск
        await perform_text_search(message, telegram_user_id, search_query)

    except Exception as e:
        logger.error(f"Error in search_text_handler: {e}")
        await message.answer(settings.error_message)


@router.callback_query(F.data.startswith("search_result_"))
async def search_result_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик выбора результата поиска."""
    try:
        # Получаем telegram_user_id из события
        telegram_user_id = callback.from_user.id

        # Извлекаем ID пункта меню из результата поиска
        menu_item_id = int(callback.data.split("_")[2])

        # Загружаем контент
        menu_content = await menu_service.get_menu_content(telegram_user_id, menu_item_id)

        if not menu_content:
            await callback.answer("Результат поиска больше недоступен", show_alert=True)
            return

        # Отправляем контент
        success = await menu_service.send_content_user(menu_content, callback)

        if success:
            # Создаем клавиатуру действий
            from ..utils.keyboards import create_content_actions_keyboard

            keyboard = create_content_actions_keyboard(menu_item_id)

            await callback.message.edit_reply_markup(reply_markup=keyboard)

            # Обновляем состояние
            await state.set_state(UserStates.content_view)
            await state.update_data(
                viewed_content_id=menu_item_id, content_title=menu_content.get("title", "Материал"), from_search=True
            )

            # Логируем переход к контенту
            await activity_service.log_content_view(
                telegram_user_id, menu_item_id, menu_content.get("title", "Unknown")
            )

        await callback.answer()

    except ValueError:
        await callback.answer("Неверный формат данных", show_alert=True)
    except Exception as e:
        logger.error(f"Error in search_result_handler: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


async def perform_search(callback: types.CallbackQuery, telegram_user_id: int, search_query: str, page: int = 1):
    """Выполняет поиск и отправляет результаты."""
    try:
        # Вызываем поиск через API
        search_results = await menu_service.search_materials(telegram_user_id, search_query, limit=5, page=page)

        if not search_results:
            await callback.message.edit_text(
                text=f"😔 По запросу «{search_query}» ничего не найдено.\n\n"
                "Попробуйте изменить формулировку или использовать синонимы.",
                reply_markup=create_back_menu_keyboard(),
                parse_mode=settings.parse_mode,
            )
            await callback.answer("Результаты не найдены", show_alert=True)
            return

        # Логируем поисковый запрос
        await activity_service.log_search(telegram_user_id, search_query)

        # Отправляем результаты поиска
        await send_search_results(callback, search_query, search_results, page)

        await callback.answer()

    except Exception as e:
        logger.error(f"Error performing search: {e}")
        await callback.message.edit_text(
            text="😔 Произошла ошибка при поиске. Попробуйте позже.",
            reply_markup=create_back_menu_keyboard(),
            parse_mode=settings.parse_mode,
        )


async def perform_text_search(message: types.Message, telegram_user_id: int, search_query: str):
    """Выполняет поиск по текстовому запросу."""
    try:
        # Вызываем поиск через API
        search_results = await menu_service.search_materials(telegram_user_id, search_query, limit=5, page=1)

        if not search_results:
            await message.answer(
                text=f"😔 По запросу «{search_query}» ничего не найдено.\n\n"
                "Попробуйте изменить формулировку или использовать синонимы.",
                parse_mode=settings.parse_mode,
            )
            return

        # Логируем поисковый запрос
        await activity_service.log_search(telegram_user_id, search_query)

        # Отправляем результаты поиска
        await send_text_search_results(message, search_query, search_results)

    except Exception as e:
        logger.error(f"Error performing text search: {e}")
        await message.answer("😔 Произошла ошибка при поиске. Попробуйте позже.")


async def send_search_results(
    callback: types.CallbackQuery, search_query: str, results: List[Dict[str, Any]], current_page: int
):
    """Отправляет результаты поиска через callback."""
    # Определяем общее количество страниц
    total_results = len(results)
    total_pages = (total_results + 4) // 5  # Округление вверх

    # Создаем текстовое сообщение
    message_text = f"🔍 Результаты поиска «{search_query}»:\n\n"

    start_index = (current_page - 1) * 5
    end_index = min(start_index + 5, total_results)

    for i in range(start_index, end_index):
        result = results[i]
        message_text += f"{i + 1}. {result['title']}\n"

        if result.get("description"):
            description = result["description"][:100]
            message_text += f"   {description}{'...' if len(result['description']) > 100 else ''}\n"
        message_text += "\n"

    # Создаем клавиатуру с результатами
    keyboard = create_search_results_keyboard(results[start_index:end_index])

    # Добавляем пагинацию если нужно
    if total_pages > 1:
        keyboard = create_search_pagination_keyboard(current_page, total_pages, search_query, keyboard)

    await callback.message.edit_text(
        text=message_text,
        reply_markup=keyboard,
        parse_mode=settings.parse_mode,
        disable_web_page_preview=settings.disable_web_page_preview,
    )


async def send_text_search_results(message: types.Message, search_query: str, results: List[Dict[str, Any]]):
    """Отправляет результаты поиска через новое сообщение."""
    # Создаем текстовое сообщение
    message_text = f"🔍 Результаты поиска «{search_query}»:\n\n"

    for i, result in enumerate(results[:5], 1):  # Показываем первые 5 результатов
        message_text += f"{i}. {result['title']}\n"

        if result.get("description"):
            description = result["description"][:100]
            message_text += f"   {description}{'...' if len(result['description']) > 100 else ''}\n"
        message_text += "\n"

    # Создаем клавиатуру с результатами
    keyboard = create_search_results_keyboard(results[:5])

    await message.answer(
        text=message_text,
        reply_markup=keyboard,
        parse_mode=settings.parse_mode,
        disable_web_page_preview=settings.disable_web_page_preview,
    )
