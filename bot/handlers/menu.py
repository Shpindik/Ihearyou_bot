"""Обработчики навигации по меню."""

import logging

from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from ..config import settings
from ..services.menu_service import MenuService
from ..services.user_activity_service import UserActivityService
from ..utils.keyboards import create_content_actions_keyboard, create_menu_keyboard
from .start import UserStates


logger = logging.getLogger(__name__)

router = Router()
menu_service = MenuService()
activity_adviser = UserActivityService()


@router.callback_query(F.data.startswith("menu_"))
async def menu_navigation_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик навигации по меню."""
    try:
        # Получаем telegram_user_id из события
        telegram_user_id = callback.from_user.id

        # Извлекаем ID пункта меню
        menu_item_id = int(callback.data.split("_")[1])

        # Загружаем контент пункта меню
        menu_content = await menu_service.get_menu_content(telegram_user_id, menu_item_id)

        if not menu_content:
            await callback.answer("Пункт меню не найден", show_alert=True)
            return

        item_type = menu_content.get("item_type")
        logger.debug(f"Menu item {menu_item_id} has type: {item_type}, content: {menu_content}")

        if item_type == "navigation":
            # Навигационный пункт - показываем дочерние элементы
            children = menu_content.get("children", [])

            if children:
                keyboard = create_menu_keyboard(children)

                message_text = menu_content.get("bot_message", "📁 Выберите раздел:")

                await callback.message.edit_text(
                    text=message_text,
                    reply_markup=keyboard,
                    parse_mode=settings.parse_mode,
                    disable_web_page_preview=settings.disable_web_page_preview,
                )

                # Обновляем состояние навигации
                await state.set_state(UserStates.menu_navigation)
                await state.update_data(current_parent=menu_item_id, parent_id=menu_content.get("parent_id"))

                # Записываем активность
                await activity_adviser.log_menu_navigation(telegram_user_id, menu_item_id)

            else:
                await callback.answer("Нет доступных подразделов", show_alert=True)

        elif item_type == "content":
            # Контентный пункт - показываем контент
            success = await menu_service.send_content_user(menu_content, callback)

            if success:
                # Создаем клавиатуру действий для контента
                keyboard = create_content_actions_keyboard(menu_item_id)

                # Добавляем кнопки действий
                await callback.message.edit_reply_markup(reply_markup=keyboard)

                # Обновляем состояние просмотра контента
                await state.set_state(UserStates.content_view)
                await state.update_data(
                    viewed_content_id=menu_item_id, content_title=menu_content.get("title", "Материал")
                )

                # Записываем активность просмотра контента
                await activity_adviser.log_content_view(
                    telegram_user_id, menu_item_id, menu_content.get("title", "Unknown")
                )

                await callback.answer()
            else:
                await callback.answer("Ошибка загрузки контента", show_alert=True)
        else:
            # Если тип неопределен или неизвестен, пытаемся обработать как контент
            logger.warning(f"Unknown menu item type: {item_type} for item {menu_item_id}")
            success = await menu_service.send_content_user(menu_content, callback)
            
            if success:
                # Создаем клавиатуру действий для контента
                keyboard = create_content_actions_keyboard(menu_item_id)
                
                # Добавляем кнопки действий
                await callback.message.edit_reply_markup(reply_markup=keyboard)
                
                # Обновляем состояние просмотра контента
                await state.set_state(UserStates.content_view)
                await state.update_data(
                    viewed_content_id=menu_item_id, content_title=menu_content.get("title", "Материал")
                )
                
                await callback.answer()
            else:
                await callback.answer("Ошибка обработки пункта меню", show_alert=True)

    except ValueError:
        await callback.answer("Неверный формат данных", show_alert=True)
    except Exception as e:
        logger.error(f"Error in menu_navigation_handler: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)


@router.callback_query(F.data.startswith("content_menu_"))
async def content_menu_handler(callback: types.CallbackQuery, state: FSMContext):
    """Обработчик возврата к меню из контента."""
    try:
        # Получаем telegram_user_id из события
        telegram_user_id = callback.from_user.id

        # Извлекаем ID контента
        content_id = int(callback.data.split("_")[2])

        # Получаем данные контента для определения родительского пункта
        menu_content = await menu_service.get_menu_content(telegram_user_id, content_id)

        if not menu_content:
            await callback.answer("Контент не найден", show_alert=True)
            return

        parent_id = menu_content.get("parent_id")

        # Загружаем родительское меню
        menu_items = await menu_service.get_menu_items(telegram_user_id, parent_id)

        if menu_items:
            keyboard = create_menu_keyboard(menu_items)

            message_text = "📁 Перейдите к нужному разделу:"

            await callback.message.edit_text(
                text=message_text,
                reply_markup=keyboard,
                parse_mode=settings.parse_mode,
                disable_web_page_preview=settings.disable_web_page_preview,
            )

            # Обновляем состояние
            await state.set_state(UserStates.menu_navigation)
            await state.update_data(current_parent=content_id, parent_id=parent_id)

        else:
            # Если нет родительского меню, возвращаемся к выбору пути
            from ..utils.keyboards import create_main_menu_keyboard

            await callback.message.edit_text(
                text=settings.welcome_message,
                reply_markup=create_main_menu_keyboard(),
                parse_mode=settings.parse_mode,
                disable_web_page_preview=settings.disable_web_page_preview,
            )
            await state.set_state(UserStates.main_menu)

        await callback.answer()

    except ValueError:
        await callback.answer("Неверный формат данных", show_alert=True)
    except Exception as e:
        logger.error(f"Error in content_menu_handler: {e}")
        await callback.answer("Произошла ошибка", show_alert=True)
