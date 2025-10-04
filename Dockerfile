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

# Frontend
FROM node:20-slim AS frontend
WORKDIR /app
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci && \
    rm -rf package-lock.json node_modules && \
    npm install
COPY frontend/ .
ARG VITE_API_URL=http://localhost:8001/api
ENV VITE_API_URL=${VITE_API_URL}
RUN npm run build
RUN npm install -g serve
EXPOSE 3001
CMD ["serve", "-s", "dist", "-l", "3001"]