"""Конфигурация приложения и переменные окружения."""

from typing import Optional

from fastapi_mail import ConnectionConfig
from pydantic import EmailStr, Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Настройки приложения."""

    # База данных
    database_url: str = Field(description="URL подключения к PostgreSQL")
    postgres_password: Optional[str] = Field(default=None, description="Пароль PostgreSQL")
    postgres_user: Optional[str] = Field(default=None, description="Пользователь PostgreSQL")
    postgres_db: Optional[str] = Field(default=None, description="База данных PostgreSQL")

    # JWT настройки
    jwt_secret_key: str = Field(description="Секретный ключ для JWT токенов")
    jwt_algorithm: str = Field(default="HS256", description="Алгоритм шифрования JWT")
    jwt_access_token_expire_minutes: int = Field(default=60, description="Время жизни access токена в минутах")
    jwt_refresh_token_expire_days: int = Field(default=7, description="Время жизни refresh токена в днях")

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
    admin_username: str = Field(default="admin", description="Имя пользователя администратора по умолчанию")
    admin_password: str = Field(default="admin12345", description="Пароль администратора по умолчанию")
    admin_email: Optional[EmailStr] = Field(
        default="admin@yourapp.com", description="Email администратора по умолчанию"
    )

    # Email настройки
    mail_username: EmailStr = Field(default="admin@yourapp.com", description="Email для отправки писем")
    mail_password: str = Field(default="your_app_password", description="Пароль приложения для email")
    mail_from: EmailStr = Field(default="noreply@yourapp.com", description="Email отправителя")
    mail_port: int = Field(default=587, description="SMTP порт")
    mail_server: str = Field(default="smtp.gmail.com", description="SMTP сервер")
    mail_tls: bool = Field(default=True, description="Использовать TLS")
    mail_ssl: bool = Field(default=False, description="Использовать SSL")

    # Frontend URL для ссылок в письмах
    frontend_url: str = Field(default="http://localhost:3000", description="URL фронтенда для ссылок")

    # Email валидация
    email_dns_check: bool = Field(default=True, description="Проверять DNS при валидации email")

    # Telegram Bot
    bot_token: Optional[str] = Field(default=None, description="Токен Telegram бота")

    # Медиафайлы - дополнительные настройки (не используется)
    # media_storage_path: str = Field(
    #     default="./media",
    #     description="Путь для хранения локальных медиафайлов"
    # )

    # Логирование
    log_level: str = Field(default="INFO", description="Уровень логирования")
    # log_file_path: Optional[str] = Field(
    #     default=None,
    #     description="Путь к файлу логов"
    # )

    # Redis (не используется)
    # redis_url: Optional[str] = Field(
    #     default=None,
    #     description="URL подключения к Redis"
    # )

    def email_conf(self) -> ConnectionConfig:
        """Конфигурация для FastAPI-Mail"""
        return ConnectionConfig(
            MAIL_USERNAME=self.mail_username,
            MAIL_PASSWORD=self.mail_password,
            MAIL_FROM=self.mail_from,
            MAIL_PORT=self.mail_port,
            MAIL_SERVER=self.mail_server,
            MAIL_STARTTLS=self.mail_tls,
            MAIL_SSL_TLS=self.mail_ssl,
        )

    class Config:
        """Конфигурация Pydantic."""

        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Глобальный экземпляр настроек
settings = Settings()
