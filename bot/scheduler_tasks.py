"""MVP: Простые задачи планировщика для автоматических напоминаний."""

import os
import aiohttp
from datetime import datetime, timezone
from typing import List, Dict, Optional
from telegram import Bot
from telegram.error import (
    BadRequest,
    Forbidden,
    NetworkError,
    TelegramError,
    TimedOut,
    Unauthorized,
)


async def send_reminders_cron():
    """MVP: Напоминания неактивным пользователям в 10:00 утра.
    
    Логика:
    1. Получение неактивных пользователей через Bot API
    2. Получение активного шаблона сообщения
    3. Персонализированная отправка через Telegram Bot API
    """
    try:
        bot_token = os.getenv("BOT_TOKEN")
        api_base_url = os.getenv("API_BASE_URL", "http://bot_api:8000/api/v1")
        
        if not bot_token:
            print("❌ BOT_TOKEN не найден в переменных окружения")
            return
            
        # Инициализируем бота для отправки
        bot = Bot(token=bot_token)
        
        async with aiohttp.ClientSession() as session:
            print("🎯 MVP: Начало отправки напоминаний...")
            
            # Шаг 1: Получение активного шаблона
            template_data = await _get_active_template(session, api_base_url)
            if not template_data:
                print("❌ Активный шаблон не найден")
                return
                
            print(f"📝 Используется шаблон: '{template_data['name']}'")
            
            # Шаг 2: Получение неактивных пользователей
            inactive_users = await _get_inactive_users(session, api_base_url)
            if not inactive_users:
                print("✅ Неактивных пользователей не найдено")
                return
                
            print(f"👥 Найдено {len(inactive_users)} неактивных пользователей")
            
            # Шаг 3: Отправка персонализированных сообщений
            sent_count = 0
            failed_count = 0
            
            for user in inactive_users:
                try:
                    # Персонализируем сообщение
                    personalized_message = _personalize_message(
                        template_data['message_template'], 
                        user['first_name']
                    )
                    
                    await bot.send_message(
                        chat_id=user['telegram_user_id'],
                        text=personalized_message,
                        parse_mode="HTML"
                    )
                    
                    # Обновляем статус отправки в базе данных
                    await _update_reminder_status(session, api_base_url, user['telegram_user_id'])
                    
                    sent_count += 1
                    print(f"✅ Напоминание отправлено: {user['first_name']}")
                    
                except Forbidden:
                    failed_count += 1
                    print(f"❌ Пользователь {user['first_name']} заблокировал бота")
                    
                except (BadRequest, NetworkError, TimedOut) as e:
                    failed_count += 1
                    print(f"❌ Ошибка отправки для {user['first_name']}: {e}")
                    
                except Exception as e:
                    failed_count += 1
                    print(f"❌ Неожиданная ошибка для {user['first_name']}: {e}")
            
            print(f"🎉 MVP Завершено: отправлено {sent_count}, ошибок {failed_count}")
                
    except Exception as e:
        print(f"❌ Критическая ошибка в send_reminders_cron: {e}")
        import traceback
        traceback.print_exc()


async def _get_active_template(session: aiohttp.ClientSession, api_base_url: str) -> Optional[Dict]:
    """Получить активный шаблон через API."""
    try:
        url = f"{api_base_url}/telegram-user/active-template"
        
        async with session.get(url) as response:
            if response.status == 200:
                template_data = await response.json()
                return template_data
            elif response.status == 404:
                print("⚠️ Активные шаблоны не найдены")
                return None
            else:
                print(f"❌ Ошибка получения шаблона: {response.status}")
                return None
                
    except Exception as e:
        print(f"❌ Ошибка запроса шаблона: {e}")
        return None


async def _get_inactive_users(session: aiohttp.ClientSession, api_base_url: str) -> List[Dict]:
    """Получить неактивных пользователей через API."""
    try:
        url = f"{api_base_url}/telegram-user/inactive-users"
        params = {
            "inactive_days": 10,  # Неактивен более 10 дней
            "days_since_last_reminder": 7  # Последнее напоминание было более 7 дней назад
        }
        
        async with session.get(url, params=params) as response:
            if response.status == 200:
                users_data = await response.json()
                return users_data
            else:
                print(f"❌ Ошибка получения неактивных пользователей: {response.status}")
                return []
                
    except Exception as e:
        print(f"❌ Ошибка запроса неактивных пользователей: {e}")
        return []


def _personalize_message(template: str, first_name: str) -> str:
    """Простая персонализация сообщения."""
    return template.replace("{first_name}", first_name)


async def _update_reminder_status(session: aiohttp.ClientSession, api_base_url: str, telegram_user_id: int) -> None:
    """Обновить статус отправки напоминания в базе данных."""
    try:
        url = f"{api_base_url}/telegram-user/update-reminder-status"
        params = {"telegram_user_id": telegram_user_id}
        
        async with session.post(url, params=params) as response:
            if response.status == 200:
                print(f"📝 Статус напоминания обновлен для пользователя {telegram_user_id}")
            else:
                print(f"⚠️ Не удалось обновить статус для пользователя {telegram_user_id}: {response.status}")
                
    except Exception as e:
        print(f"❌ Ошибка обновления статуса для пользователя {telegram_user_id}: {e}")


async def cleanup_old_notifications():
    """MVP: Очистка старых уведомлений через API."""
    print("🧹 MVP: Запрос очистки старых уведомлений...")
    
    try:
        api_base_url = os.getenv("API_BASE_URL", "http://bot_api:8000/api/v1")
        
        async with aiohttp.ClientSession() as session:
            # Примечание: Для этого может понадобиться специальный endpoint
            # пока просто логируем для MVP
            print("✅ MVP: Очистка уведомлений (заглушка)")
            
    except Exception as e:
        print(f"❌ MVP: Ошибка очистки уведомлений: {e}")


async def notification_statistics_report():
    """MVP: Получение статистики уведомлений через API."""
    print("📊 MVP: Запрос статистики уведомлений...")
    
    try:
        api_base_url = os.getenv("API_BASE_URL", "http://bot_api:8000/api/v1")
        
        async with aiohttp.ClientSession() as session:
            # Примечание: Для этого может понадобиться специальный endpoint
            print("✅ MVP: Статистика получена (заглушка)")
            
    except Exception as e:
        print(f"❌ MVP: Ошибка получения статистики: {e}")


async def health_check_notifications():
    """MVP: Проверка здоровья системы уведомлений."""
    print("🔍 MVP: Проверка здоровья системы...")
    
    try:
        bot_token = os.getenv("BOT_TOKEN")
        if not bot_token:
            print("❌ BOT_TOKEN не найден - система недоступна")
            return False
            
        # Проверяем доступность телеграм API
        bot = Bot(token=bot_token)
        bot_info = await bot.get_me()
        print(f"✅ MVP: Telegram Bot API доступен: @{bot_info.username}")
        
        # Проверяем доступность backend API
        api_base_url = os.getenv("API_BASE_URL", "http://bot_api:8000/api/v1")
        
        async with aiohttp.ClientSession() as session:
            url = f"{api_base_url}/telegram-user/inactive-users"
            params = {"inactive_days": 1, "days_since_last_reminder": 1}
            
            async with session.get(url, params=params) as response:
                if response.status in [200, 404]:
                    print("✅ MVP: Backend API доступен")
                    return True
                else:
                    print(f"⚠️ MVP: Backend API отвечает с ошибкой: {response.status}")
                    return False
        
    except Exception as e:
        print(f"❌ MVP: Ошибка проверки здоровья: {e}")
        return False