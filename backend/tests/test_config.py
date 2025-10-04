"""Тестовая конфигурация приложения."""

from typing import Optional

from fastapi_mail import ConnectionConfig
from pydantic import EmailStr, Field
from pydantic_settings import BaseSettings


class TestSettings(BaseSettings):
    """Тестовые настройки приложения."""

    # База данных
    database_url: str = Field(default="postgresql+asyncpg://test:test@localhost/testdb", description="URL подключения к тестовой PostgreSQL")
    postgres_password: Optional[str] = Field(default="test", description="Пароль тестовой PostgreSQL")
    postgres_user: Optional[str] = Field(default="test", description="Пользователь тестовой PostgreSQL")
    postgres_db: Optional[str] = Field(default="testdb", description="Тестовая база данных PostgreSQL")

    # JWT настройки (тестовые секреты)
    jwt_secret_key: str = Field(default="test_secret_key_for_testing_only_do_not_use_in_production", description="Тестовый секретный ключ для JWT токенов")
    jwt_algorithm: str = Field(default="HS256", description="Алгоритм шифрования JWT")
    jwt_access_token_expire_minutes: int = Field(default=60, description="Время жизни access токена в минутах")
    jwt_refresh_token_expire_days: int = Field(default=7, description="Время жизни refresh токена в днях")

    # Redis
    redis_url: Optional[str] = Field(default="redis://localhost:6379/1", description="URL подключения к тестовому Redis")

    # API порт
    bot_api_port: int = Field(default=8001, description="Порт API бота")

    # Окружение
    environment: str = Field(default="testing", description="Тестовое окружение приложения")
    debug: bool = Field(default=True, description="Режим отладки для тестов")

    # Frontend настройки
    frontend_api_url: str = Field(default="http://localhost:8001/api", description="URL API для фронтенда")
    frontend_port: int = Field(default=3001, description="Порт фронтенда")

    # Администратор по умолчанию (тестовый)
    admin_username: str = Field(default="testadmin", description="Имя пользователя тестового администратора")
    admin_password: str = Field(default="testpassword123", description="Пароль тестового администратора")
    admin_email: Optional[EmailStr] = Field(default="testadmin@example.com", description="Email тестового администратора")

    # Email настройки (тестовые)
    mail_username: EmailStr = Field(default="test@example.com", description="Тестовый email для отправки писем")
    mail_password: str = Field(default="test_password_change_me", description="Тестовый пароль приложения для email")
    mail_from: EmailStr = Field(default="test@example.com", description="Тестовый email отправителя")
    mail_port: int = Field(default=587, description="SMTP порт")
    mail_server: str = Field(default="smtp.test.com", description="Тестовый SMTP сервер")
    mail_tls: bool = Field(default=True, description="Использовать TLS")
    mail_ssl: bool = Field(default=False, description="Использовать SSL")

    # Frontend URL для ссылок в письмах
    frontend_url: str = Field(default="http://localhost:3000", description="URL фронтенда для ссылок")

    # Email валидация (отключена для тестов)
    email_dns_check: bool = Field(default=False, description="Проверка DNS для email (отключена в тестах)")

    # Логирование
    log_level: str = Field(default="DEBUG", description="Уровень логирования для тестов")

    def email_conf(self) -> ConnectionConfig:
        """Тестовая конфигурация для FastAPI-Mail"""
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
        """Конфигурация Pydantic для тестов."""

        env_file = ".env.test"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Глобальный экземпляр тестовых настроек
test_settings = TestSettings()
