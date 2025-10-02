from typing import Any, Dict, Optional

from aiogram.types import CallbackQuery, Message
from states import NavigationState

# Глобальное состояние навигации для всех пользователей
navigation_states: Dict[int, NavigationState] = {}


def get_or_create_navigation_state(user_id: int) -> NavigationState:
    """Получает или создает состояние навигации для пользователя"""
    if user_id not in navigation_states:
        navigation_states[user_id] = NavigationState()
    return navigation_states[user_id]


def add_navigation_state(user_id: int, message_text: str, reply_markup=None, meta: Optional[Dict[str, Any]] = None):
    """Добавляет состояние в историю навигации"""
    nav_state = get_or_create_navigation_state(user_id)
    nav_state.add_state(message_text, reply_markup, meta)



async def send_message_with_navigation(message: Message, text: str, reply_markup=None, meta: Optional[Dict[str, Any]] = None):
    """Отправляет сообщение и добавляет состояние в навигацию"""
    user_id = message.from_user.id
    add_navigation_state(user_id, text, reply_markup, meta)
    return await message.answer(text, reply_markup=reply_markup)


async def edit_message(
    callback: CallbackQuery,
    text: str,
    reply_markup=None,
    add_to_history: bool = True,
    meta: Optional[Dict[str, Any]] = None,
):
    """Редактирует сообщение и добавляет состояние в навигацию"""
    user_id = callback.from_user.id

    try:
        # Проверяем, изменился ли контент или клавиатура
        current_text = callback.message.text
        current_markup = callback.message.reply_markup

        # Если текст и клавиатура совпадают, не редактируем
        if current_text == text and current_markup == reply_markup:
            return

        await callback.message.edit_text(text=text, reply_markup=reply_markup)
        # Добавляем состояние в навигацию только после успешного редактирования
        if add_to_history:
            meta_to_store: Dict[str, Any] = (meta or {}).copy()
            try:
                meta_to_store.setdefault("message_id", callback.message.message_id)
                meta_to_store.setdefault("chat_id", callback.message.chat.id)
            except Exception:
                pass
            add_navigation_state(user_id, text, reply_markup, meta_to_store)
    except Exception:
        # Если редактирование не удалось, отправляем новое сообщение
        sent = await callback.message.answer(text, reply_markup=reply_markup)
        # Добавляем состояние в навигацию
        if add_to_history:
            meta_to_store: Dict[str, Any] = (meta or {}).copy()
            try:
                meta_to_store.setdefault("message_id", sent.message_id)
                meta_to_store.setdefault("chat_id", sent.chat.id)
            except Exception:
                pass
            add_navigation_state(user_id, text, reply_markup, meta_to_store)


