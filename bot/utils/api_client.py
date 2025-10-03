"""HTTP клиент для работы с API Backend."""

import asyncio
import logging
from typing import Any, Dict, Optional

import aiohttp
from aiohttp import ClientSession, ClientTimeout


class APIClient:
    """Асинхронный клиент для работы с API Backend."""

    def __init__(self, base_url: str, timeout: int = 30, retries: int = 3):
        """Инициализация API клиента.

        Args:
            base_url: Базовый URL API
            timeout: Таймаут запросов в секундах
            retries: Количество повторных попыток
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.retries = retries
        self.logger = logging.getLogger(__name__)

    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Выполняем HTTP запрос с повторными попытками.

        Args:
            method: HTTP метод (GET, POST, PUT, DELETE)
            endpoint: Путь к эндпоинту
            data: Данные для отправки в теле запроса
            params: URL параметры
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        timeout = ClientTimeout(total=self.timeout)

        for attempt in range(self.retries):
            try:
                async with ClientSession(timeout=timeout) as session:
                    async with session.request(
                        method=method,
                        url=url,
                        json=data,
                        headers={"Content-Type": "application/json"},
                        params=params and {k: v for k, v in params.items() if v is not None},
                    ) as response:
                        response_data = await response.json()

                        if response.status >= 400:
                            error_msg = response_data.get("detail", "Unknown error")
                            raise APIClientError(f"API Error {response.status}: {error_msg}")

                        return response_data

            except aiohttp.ClientError as e:
                self.logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt == self.retries - 1:
                    raise APIClientError(f"Request failed after {self.retries} attempts: {e}")

                await asyncio.sleep(2**attempt)  # Exponential backoff

    async def __aenter__(self):
        """Поддержка контекстного менеджера."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Очистка ресурсов."""
        pass


class APIClientError(Exception):
    """Ошибка API клиента."""

    pass


# Экземпляр клиента по умолчанию
from ..config import settings  # noqa: E402


api_client = APIClient(base_url=settings.api_base_url, timeout=settings.api_timeout, retries=settings.api_retries)
