"""Утилиты для отправки email уведомлений."""

from __future__ import annotations

from fastapi import HTTPException, status
from fastapi_mail import FastMail, MessageSchema

from backend.core.config import settings


class EmailService:
    """Сервис для отправки email уведомлений."""

    def __init__(self):
        """Инициализация сервиса email уведомлений."""
        self.fastmail = FastMail(settings.email_conf())

    async def send_password_reset_email(self, email: str, reset_token: str, admin_name: str = "Администратор") -> None:
        """Отправляет письмо с ссылкой для восстановления пароля.

        Args:
            email: Email адрес получателя
            reset_token: Токен для восстановления пароля
            admin_name: Имя администратора для персонализации

        Raises:
            HTTPException: При ошибке отправки письма
        """
        try:
            reset_url = f"{settings.frontend_url}/admin/reset-password?token={reset_token}"

            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Восстановление пароля</title>
            </head>
            <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                <h2>Восстановление пароля</h2>
                <p>Здравствуйте, {admin_name}!</p>
                <p>Вы запросили восстановление пароля для админ-панели.</p>
                <p>Нажмите на кнопку ниже для смены пароля:</p>
                <p style="text-align: center; margin: 30px 0;">
                    <a href="{reset_url}" 
                       style="background-color: #007bff; color: white; padding: 12px 24px; 
                              text-decoration: none; border-radius: 5px; display: inline-block;">
                        Сменить пароль
                    </a>
                </p>
                <p>Или скопируйте ссылку: <code>{reset_url}</code></p>
                <p><strong>Важно:</strong> Ссылка действует 1 час с момента отправки письма.</p>
                <hr>
                <p style="font-size: 12px; color: #666;">
                    Если вы не запрашивали восстановление пароля, проигнорируйте это письмо.
                </p>
            </body>
            </html>
            """

            message = MessageSchema(
                subject="Восстановление пароля - Админ-панель", recipients=[email], body=html_body, subtype="html"
            )

            await self.fastmail.send_message(message)

        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Ошибка отправки письма: {str(e)}"
            )


email_service = EmailService()
