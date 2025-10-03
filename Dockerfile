FROM python:3.12-slim AS base

# Установка системных утилит для health check
RUN apt-get update && apt-get install -y \
    procps \
    curl \
    && rm -rf /var/lib/apt/lists/*

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Установка Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Poetry конфигурация для Docker
RUN poetry config virtualenvs.create false \
    && poetry config virtualenvs.in-project false

# Копирование зависимостей
COPY pyproject.toml poetry.lock ./

# Установка зависимостей
RUN poetry install --only=main --no-root

# Bot
FROM base AS bot
COPY bot ./bot
EXPOSE 8080

CMD ["python", "-m", "bot.main"]

# API  
FROM base AS admin
COPY backend ./backend
COPY alembic ./alembic
COPY alembic.ini ./
EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]