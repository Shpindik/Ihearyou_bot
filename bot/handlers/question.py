"""Обработчики вопросов пользователей."""

import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from ..config import settings
from ..services.question_service import QuestionService
from ..services.user_activity_service import UserActivityService
from ..utils.keyboards import create_back_menu_keyboard
from .start import UserStates


logger = logging.getLogger(__name__)

router = Router()
question_service = QuestionService()
activity_service = UserActivityService()


@router.callback_query(F.data == "ask_question")
async def ask_question_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик начала создания вопроса."""
    try:
        await state.set_state(UserStates.question_input)

        message_text = (
            "❓ Задайте свой вопрос:\n\n"
            "Мы понимаем, что у вас могут быть важные вопросы о слухе вашего ребенка "
            "или собственном слухе. Опишите вашу ситуацию как можно подробнее, "
            "и наши специалисты обязательно ответят.\n\n"
            "📝 Введите ваш вопрос (до 2000 символов):\n"
            "⬅️ Для отмены используйте команду /start"
        )

        # Создаем клавиатуру с кнопкой отмены
        from aiogram.utils.keyboard import InlineKeyboardBuilder
        
        builder = InlineKeyboardBuilder()
        builder.button(text="🏠 Главное меню", callback_data="home")
        
        keyboard = builder.as_markup()

        await callback.message.edit_text(
            text=message_text,
            parse_mode=settings.parse_mode,
            reply_markup=keyboard,
        )

        await callback.answer()

    except Exception as e:
        logger.error(f"Error in ask_question_handler: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.message(F.text, lambda message: len(message.text) >= 10)
async def question_input_handler(message: types.Message, state: FSMContext):
    """Обработчик текста вопроса."""
    try:
        # Получаем telegram_user_id из события
        telegram_user_id = message.from_user.id
        
        current_state = await state.get_state()

        if current_state != UserStates.question_input:
            # Если пользователь не в состоянии ввода вопроса, игнорируем
            return

        question_text = message.text.strip()

        if len(question_text) < 10:
            await message.answer(
                "📝 Вопрос слишком короткий. Пожалуйста, напишите более подробно " "(минимум 10 символов).",
                parse_mode=settings.parse_mode,
            )
            return

        if len(question_text) > 2000:
            await message.answer(
                "📝 Вопрос слишком длинный. Пожалуйста, сократите его " "до 2000 символов.",
                parse_mode=settings.parse_mode,
            )
            return

        # Проверяем качество вопроса (простая проверка)
        if not is_valid_question_text(question_text):
            await message.answer(
                "📝 Пожалуйста, введите осмысленный вопрос. "
                "Избегайте избыточного количества повторяющихся символов.",
                parse_mode=settings.parse_mode,
            )
            return

        # Отправляем вопрос через API
        question_data = await question_service.submit_question(
            telegram_user_id=telegram_user_id, question_text=question_text
        )

        if question_data:
            # Логируем активность
            await activity_service.log_question_ask(telegram_user_id)

            # Показываем подтверждение
            confirmation_text = (
                "✅ Ваш вопрос успешно отправлен!\n\n"
                "📨 Наши специалисты рассмотрят ваш вопрос и обязательно "
                "ответят в ближайшее время. Спасибо за доверие!\n\n"
                "🔄 Если у вас есть еще вопросы, можете задать их через "
                "соответствующую кнопку в меню."
            )

            keyboard = create_back_menu_keyboard()
            await message.answer(
                text=confirmation_text, parse_mode=settings.parse_mode, reply_markup=keyboard
            )

            await state.clear()
            await state.set_state(UserStates.main_menu)  # Явно устанавливаем состояние главного меню

        else:
            keyboard = create_back_menu_keyboard()
            await message.answer(
                text="😔 Произошла ошибка при отправке вопроса. Попробуйте позже или обратитесь к администратору.",
                parse_mode=settings.parse_mode,
                reply_markup=keyboard,
            )
            await state.set_state(UserStates.main_menu)

    except Exception as e:
        logger.error(f"Error in question_input_handler: {e}")
        keyboard = create_back_menu_keyboard()
        await message.answer(
            text=settings.error_message, 
            parse_mode=settings.parse_mode,
            reply_markup=keyboard
        )
        await state.set_state(UserStates.main_menu)


@router.message(F.text, lambda message: len(message.text) < 10)
async def short_question_handler(message: types.Message, state: FSMContext):
    """Обработчик слишком коротких сообщений в режиме ввода вопроса."""
    current_state = await state.get_state()

    if current_state == UserStates.question_input:
        await message.answer(
            "📝 Вопрос слишком короткий. Пожалуйста, опишите вашу ситуацию более подробно (минимум 10 символов).",
            parse_mode=settings.parse_mode,
        )
    else:
        # Если пользователь не в состоянии ввода вопроса, предлагаем главное меню
        keyboard = create_back_menu_keyboard()
        await message.answer(
            "📝 Ваше сообщение слишком короткое. Используйте меню для навигации:",
            parse_mode=settings.parse_mode,
            reply_markup=keyboard
        )
        await state.set_state(UserStates.main_menu)


@router.message(F.text.startswith("/start"))
async def start_command_handler(message: types.Message, state: FSMContext):
    """Обработчик команды /start в процессе ввода вопроса."""
    await state.clear()
    await state.set_state(UserStates.main_menu)
    
    from ..utils.keyboards import create_main_menu_keyboard
    keyboard = create_main_menu_keyboard()
    
    await message.answer(
        text=settings.welcome_message,
        parse_mode=settings.parse_mode,
        reply_markup=keyboard,
        disable_web_page_preview=settings.disable_web_page_preview,
    )


def is_valid_question_text(text: str) -> bool:
    """Проверяет валидность текста вопроса.

    Args:
        text: Текст вопроса

    Returns:
        True если текст валиден
    """
    # Проверяем на избыточное количество повторяющихся символов
    if len(set(text.replace(" ", ""))) < 3:
        return False

    # Проверяем на спам-паттерны
    spam_patterns = ["aaaa", "bbbb", "ээээ", "ееее"]
    text_lower = text.lower()

    for pattern in spam_patterns:
        if pattern in text_lower:
            return False

    return True

