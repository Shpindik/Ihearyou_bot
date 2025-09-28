"""Конфигурация приложения и переменные окружения."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""
    
    # База данных
    database_url: str = Field(
        description="URL подключения к PostgreSQL"
    )
    postgres_password: Optional[str] = Field(
        default=None,
        description="Пароль PostgreSQL"
    )
    postgres_user: Optional[str] = Field(
        default=None,
        description="Пользователь PostgreSQL"
    )
    postgres_db: Optional[str] = Field(
        default=None,
        description="База данных PostgreSQL"
    )
    
    # JWT настройки
    jwt_secret_key: str = Field(
        description="Секретный ключ для JWT токенов"
    )
    jwt_algorithm: str = Field(
        default="HS256",
        description="Алгоритм шифрования JWT"
    )
    jwt_access_token_expire_minutes: int = Field(
        default=60,
        description="Время жизни access токена в минутах"
    )
    jwt_refresh_token_expire_days: int = Field(
        default=7,
        description="Время жизни refresh токена в днях"
    )
    
    # Rate limiting (не используется)
    # rate_limit_enabled: bool = Field(
    #     default=True,
    #     description="Включить rate limiting"
    # )
    # rate_limit_requests_per_minute: int = Field(
    #     default=60,
    #     description="Количество запросов в минуту"
    # )
    
    # Медиафайлы (не используется)
    # media_max_file_size: int = Field(
    #     default=50 * 1024 * 1024,  # 50MB
    #     description="Максимальный размер файла в байтах"
    # )
    # media_allowed_types: str = Field(
    #     default="image/*,video/*,application/pdf",
    #     description="Разрешенные типы файлов"
    # )
    
    # Администратор по умолчанию
    admin_username: str = Field(
        default="admin",
        description="Имя пользователя администратора по умолчанию"
    )
    admin_password: str = Field(
        default="admin12345",
        description="Пароль администратора по умолчанию"
    )
    admin_email: Optional[str] = Field(
        default=None,
        description="Email администратора по умолчанию"
    )

    # Telegram Bot
    bot_token: Optional[str] = Field(
        default=None,
        description="Токен Telegram бота"
    )
    
    # Медиафайлы - дополнительные настройки (не используется)
    # media_storage_path: str = Field(
    #     default="./media",
    #     description="Путь для хранения локальных медиафайлов"
    # )

    # Логирование
    log_level: str = Field(
        default="INFO",
        description="Уровень логирования"
    )
    # log_file_path: Optional[str] = Field(
    #     default=None,
    #     description="Путь к файлу логов"
    # )

    # Redis (не используется)
    # redis_url: Optional[str] = Field(
    #     default=None,
    #     description="URL подключения к Redis"
    # )

    class Config:
        """Конфигурация Pydantic."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Глобальный экземпляр настроек
settings = Settings()
