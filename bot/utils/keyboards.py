"""Утилиты для создания клавиатур Telegram бота."""

from typing import List, Optional

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..config import settings


def create_rating_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру для оценки материала (1-5 звезд)."""
    builder = InlineKeyboardBuilder()

    for i in range(1, 6):
        builder.button(text=f"{settings.emoji_rating} {i}", callback_data=f"rate_{i}")

    builder.adjust(5)  # 5 кнопок в ряд
    return builder.as_markup()


def create_menu_keyboard(items: List[dict]) -> InlineKeyboardMarkup:
    """Создает клавиатуру с пунктами меню.

    Args:
        items: Список пунктов меню из API
    """
    builder = InlineKeyboardBuilder()

    # Динамические пункты меню
    if items:
        for item in items:
            emoji = "📂" if item.get("item_type") == "navigation" else "📄"
            text = f"{emoji} {item['title']}"

            builder.button(
                text=text[:64],  # Telegram лимит длины текста
                callback_data=f"menu_{item['id']}",
            )

    # Постоянные кнопки навигации
    builder.button(text=f"{settings.emoji_search} Поиск", callback_data="search")
    builder.button(text=f"{settings.emoji_question} Задать вопрос", callback_data="ask_question")

    # Кнопка "Назад" только если есть контент для возврата
    builder.button(text=f"{settings.emoji_back} Назад", callback_data="back")
    builder.button(text=f"{settings.emoji_home} Главное меню", callback_data="home")

    builder.adjust(1)  # Вертикальное расположение
    return builder.as_markup()


def create_back_menu_keyboard(parent_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """Создает клавиатуру для возврата в меню."""
    builder = InlineKeyboardBuilder()

    if parent_id:
        builder.button(text=f"{settings.emoji_back} Назад", callback_data=f"menu_{parent_id}")

    builder.button(text=f"{settings.emoji_home} Главное меню", callback_data="home")

    builder.button(text=f"{settings.emoji_search} Поиск", callback_data="search")

    return builder.as_markup()


def create_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Создает клавиатуру главного меню."""
    builder = InlineKeyboardBuilder()

    # Основные пункты меню
    builder.button(text="🧸 Я волнуюсь о слухе ребенка", callback_data="path_child")
    builder.button(text="👤 Я волнуюсь о своем слухе", callback_data="path_adult")

    # Постоянные кнопки навигации
    builder.button(text=f"{settings.emoji_search} Поиск", callback_data="search")
    builder.button(text=f"{settings.emoji_question} Задать вопрос", callback_data="ask_question")

    builder.adjust(1)
    return builder.as_markup()


def create_content_actions_keyboard(menu_item_id: int) -> InlineKeyboardMarkup:
    """Создает клавиатуру действий для контента."""
    builder = InlineKeyboardBuilder()

    # Кнопка оценки материала
    builder.button(text=f"{settings.emoji_rating} Оценить материал", callback_data=f"content_rating_{menu_item_id}")

    # Постоянные кнопки навигации
    builder.button(text=f"{settings.emoji_search} Поиск", callback_data="search")
    builder.button(text=f"{settings.emoji_question} Задать вопрос", callback_data="ask_question")

    # Кнопка "Назад"
    builder.button(text=f"{settings.emoji_back} Назад", callback_data=f"content_menu_{menu_item_id}")
    builder.button(text=f"{settings.emoji_home} Главное меню", callback_data="home")

    builder.adjust(1)
    return builder.as_markup()


def create_confirmation_keyboard(prefix: str) -> InlineKeyboardMarkup:
    """Создает клавиатуру подтверждения."""
    builder = InlineKeyboardBuilder()

    builder.button(text="✅ Да", callback_data=f"{prefix}_yes")
    builder.button(text="❌ Нет", callback_data=f"{prefix}_no")

    builder.adjust(1)
    return builder.as_markup()


def create_search_results_keyboard(results: List[dict]) -> InlineKeyboardMarkup:
    """Создает клавиатуру с результатами поиска."""
    builder = InlineKeyboardBuilder()

    # Динамические результаты поиска
    if results:
        for i, result in enumerate(results, 1):
            text = f"{i}. {result['title'][:50]}"
            builder.button(text=text, callback_data=f"search_result_{result['id']}")
    else:
        # Если результатов нет, показываем сообщение
        builder.button(text="📝 Результаты не найдены", callback_data="no_results")

    # Постоянные кнопки навигации
    builder.button(text=f"{settings.emoji_search} Новый поиск", callback_data="search")
    builder.button(text=f"{settings.emoji_question} Задать вопрос", callback_data="ask_question")

    # Кнопка "Назад"
    builder.button(text=f"{settings.emoji_back} Назад", callback_data="back")
    builder.button(text=f"{settings.emoji_home} Главное меню", callback_data="home")

    builder.adjust(1)
    return builder.as_markup()


def create_search_pagination_keyboard(
    current_page: int, total_pages: int, search_query: str, existing_keyboard: InlineKeyboardMarkup
) -> InlineKeyboardMarkup:
    """Добавляет пагинацию к клавиатуре поиска."""
    if total_pages <= 1:
        return existing_keyboard

    # Создаем копию существующих кнопок
    keyboard_rows = existing_keyboard.inline_keyboard.copy()

    # Добавляем строку с пагинацией
    pagination_row = []

    if current_page > 1:
        pagination_row.append(InlineKeyboardButton(text="⬅️", callback_data=f"search_page_{current_page - 1}"))

    pagination_row.append(InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data="search_info"))

    if current_page < total_pages:
        pagination_row.append(InlineKeyboardButton(text="➡️", callback_data=f"search_page_{current_page + 1}"))

    keyboard_rows.append(pagination_row)

    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)


def create_pagination_keyboard(
    current_page: int, total_pages: int, callback_prefix: str, extra_buttons: Optional[List[tuple]] = None
) -> InlineKeyboardMarkup:
    """Создает клавиатуру с пагинацией."""
    builder = InlineKeyboardBuilder()

    # Пагинация
    if total_pages > 1:
        navigation_buttons = []

        # Кнопка "Предыдущая"
        if current_page > 1:
            navigation_buttons.append(
                InlineKeyboardButton(text="⬅️", callback_data=f"{callback_prefix}_page_{current_page - 1}")
            )

        # Номер текущей страницы
        navigation_buttons.append(
            InlineKeyboardButton(text=f"{current_page}/{total_pages}", callback_data=f"{callback_prefix}_info")
        )

        # Кнопка "Следующая"
        if current_page < total_pages:
            navigation_buttons.append(
                InlineKeyboardButton(text="➡️", callback_data=f"{callback_prefix}_page_{current_page + 1}")
            )

        builder.row(*navigation_buttons)

    # Дополнительные динамические кнопки
    if extra_buttons:
        for text, callback_data in extra_buttons:
            builder.button(text=text, callback_data=callback_data)

    # Постоянные кнопки навигации
    builder.button(text=f"{settings.emoji_search} Поиск", callback_data="search")
    builder.button(text=f"{settings.emoji_question} Задать вопрос", callback_data="ask_question")

    # Кнопка "Назад"
    builder.button(text=f"{settings.emoji_back} Назад", callback_data="back")
    builder.button(text=f"{settings.emoji_home} Главное меню", callback_data="home")

    builder.adjust(1)
    return builder.as_markup()


def escape_html(text: str) -> str:
    """Экранирует HTML в тексте для Telegram."""
    if not text:
        return ""

    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
