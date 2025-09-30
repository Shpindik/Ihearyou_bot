FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Установка Poetry
RUN pip install --no-cache-dir poetry

# Копирование файлов Poetry
COPY pyproject.toml poetry.lock ./

# Установка зависимостей
RUN poetry config virtualenvs.create false \
    && poetry install --only=main --no-root

# Bot stage - только код бота
FROM base AS bot
COPY bot ./bot
CMD ["python", "bot/main.py"]

# API stage - только код бэкенда
FROM base AS admin
COPY backend ./backend
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
