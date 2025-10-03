"""Конфигурация Telegram бота."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class BotSettings(BaseSettings):
    """Настройки Telegram бота."""

    # Основные настройки бота
    bot_token: Optional[str] = Field(default=None, description="Токен Telegram бота")
    webhook_url: Optional[str] = Field(default=None, description="URL для webhook")
    webhook_secret: Optional[str] = Field(default=None, description="Секретный токен webhook")

    # API Backend
    api_base_url: str = Field(default="http://localhost:8001", description="URL API Backend")
    api_timeout: int = Field(default=30, description="Таймаут API запросов")
    api_retries: int = Field(default=3, description="Количество повторных попыток")

    # Настройки напоминаний
    inactive_days_threshold: int = Field(default=10, description="Дней неактивности для напоминаний")
    reminder_cooldown_days: int = Field(default=10, description="Интервал между напоминаниями")
    session_timeout_minutes: int = Field(default=30, description="Таймаут сессии пользователя")

    # Настройки бота
    parse_mode: str = "HTML"
    disable_web_page_preview: bool = True

    # Интервалы и время ожидания
    inactive_days_threshold: int = 10  # Дней неактивности для напоминаний
    reminder_cooldown_days: int = 10  # Интервал между напоминаниями
    session_timeout_minutes: int = 30  # Таймаут сессии пользователя

    # Тексты сообщений
    welcome_message: str = (
        "👋 Добро пожаловать в бот организации «Я тебя слышу»!\n\n"
        "Мы поможем вам найти всю необходимую информацию о слухе вашего ребенка и его развитии.\n\n"
        "Выберите направление, которое вас интересует:"
    )

    error_message: str = "😔 К сожалению, произошла ошибка. Попробуйте еще раз или обратитесь к администратору."

    # Эмодзи для кнопок
    emoji_back: str = "⬅️"
    emoji_home: str = "🏠"
    emoji_search: str = "🔍"
    emoji_question: str = "❓"
    emoji_rating: str = "⭐"
    emoji_child: str = "🧸"
    emoji_adult: str = "👤"

    class Config:
        """Конфигурация Pydantic."""

        env_file = ".env"
        env_file_encoding = "utf-8"


# Глобальный экземпляр настроек
settings = BotSettings()
