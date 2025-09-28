# Backend API - "Я тебя слышу"

## 📋 Обзор

FastAPI приложение для Telegram-бота поддержки родителей детей с нарушением слуха.

**Текущее состояние:** Базовая структура готова, большинство эндпоинтов не реализованы.

## Структура каталога
- `main.py` — точка входа FastAPI-приложения. Подключает маршруты, настраивает CORS и на старте гарантирует наличие учётной записи администратора.
- `api.py` — набор HTTP-эндпоинтов (`/api/auth/*`, `/api/users`). Здесь происходит авторизация и работа с пользователями.
- `auth.py` — вспомогательные функции для работы с паролями и JWT-токенами, а также зависимости FastAPI для проверки прав администратора.
- `database.py` — настройка асинхронного движка SQLAlchemy и фабрики сессий. Читает параметры подключения к базе из переменных окружения.
- `models.py` — декларативные описания таблиц `admin_users` и `users`.
- `schemas.py` — Pydantic-схемы для сериализации/десериализации ответов API и полезной нагрузки токена.
- `__init__.py` — делает каталог пакетом Python.

## Поток данных
1. Клиент фронтенда отправляет POST `/api/auth/login` с логином и паролем.
2. `auth.authenticate_user` проверяет пользователя в Postgres, сверяет пароль.
3. При успехе создаётся JWT-токен, который фронтенд передаёт в `Authorization: Bearer`.
4. Для защищённых эндпоинтов токен разбирается в `get_current_active_admin`; при отсутствии прав возвращается 401/403.
5. Запросы к `/api/users` обращаются к базе через `AsyncSession`, результат трансформируется в `UserResponse` и дополняется ссылкой на аватар.
6. При запросе аватара хэндлер скачивает файл с Telegram Bot API и кэширует ответ через HTTP-заголовки.

## Переменные окружения
- `ADMIN_DATABASE_URL` — полноценная строка подключения к Postgres (если не задана, собирается из `POSTGRES_*`).
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DB_HOST`, `DB_PORT` — компоненты строки подключения по умолчанию.
- `ADMIN_SECRET_KEY` — секрет для подписи JWT (обязательно сменить в продакшене).
- `ADMIN_TOKEN_EXPIRE` — время жизни токена в минутах (по умолчанию 60).
- `ADMIN_USERNAME`, `ADMIN_PASSWORD` — данные администратора, которые будут созданы/обновлены при старте сервера.
- `BOT_TOKEN` — токен Telegram-бота для получения аватаров пользователей.



## Примеры API-запросов: оценки материалов

Все запросы (кроме логина) требуют заголовок `Authorization: Bearer <TOKEN>`.

### 1) Получить токен доступа

```bash
curl -X POST \
  -d 'username=admin&password=admin12345' \
  http://localhost:8001/api/auth/login
```

Пример ответа:

```json
{
  "access_token": "<JWT>",
  "token_type": "bearer"
}
```

Сохраните значение `access_token` и используйте его в следующих запросах.

### 2) Список оценок материалов

GET `/api/article-ratings`

```bash
curl -H "Authorization: Bearer <JWT>" \
  http://localhost:8001/api/article-ratings
```

Пример ответа (обратите внимание: возвращается `fullname`, а не `user_id`):

```json
[
  {
    "id": 3,
    "fullname": "Alexander Prokofiev",
    "article_name": "Пройти онлайн-тест",
    "rating": 5,
    "created_at": "2025-09-27T07:31:04.212936Z"
  },
  {
    "id": 1,
    "fullname": "Alexander Prokofiev",
    "article_name": "Прочитать статью «8 причин»",
    "rating": 4,
    "created_at": "2025-09-27T07:22:45.801842Z"
  }
]
```

### 3) Сводка по оценкам

GET `/api/article-ratings/summary`

```bash
curl -H "Authorization: Bearer <JWT>" \
  http://localhost:8001/api/article-ratings/summary
```

Пример ответа:

```json
[
  {
    "article_name": "Прочитать статью «8 причин»",
    "ratings_count": 1,
    "avg_rating": 4.0
  },
  {
    "article_name": "Пройти онлайн-тест",
    "ratings_count": 1,
    "avg_rating": 5.0
  }
]
```

## 📁 Структура

```
backend/
├── api/                    # HTTP эндпоинты
├── core/                   # Конфигурация и утилиты
├── crud/                   # Операции с БД (только чистые crud операции)
├── models/                 # SQLAlchemy модели
├── schemas/                # Pydantic схемы
├── services/               # Сервисы со сложной логикой (будут написаны потом)
├── alembic/               # Миграции БД
├── main.py                # Точка входа
└── load_flow_data.py      # Загрузка данных
```

## 🚀 Быстрый старт

### 1. Установка

```bash
# Установка зависимостей
poetry install

# Активация окружения
poetry shell
```

### 2. Настройка

Создайте `.env` файл по примеру `.env.example`

### 3. Запуск

```bash
# Локально
poetry run uvicorn main:app --reload

# Или через Docker
docker-compose up -d
```

## 📊 База данных

### Миграции

```bash
# Создание миграции
poetry run alembic revision --autogenerate -m "описание"

# Применение миграций
poetry run alembic upgrade head
```

### Загрузка данных

```bash
# Загрузка структуры меню
poetry run python load_flow_data.py
```

## 🧪 Тестирование

### Проверка работоспособности

```bash
# Health check
curl http://localhost:8001/health
```

### Работающие эндпоинты

```bash
# Получение меню
curl "http://localhost:8001/api/v1/menu-items/?telegram_user_id=123456789"

# Контент раздела
curl "http://localhost:8001/api/v1/menu-items/1/content?telegram_user_id=123456789"

# Запись активности
curl -X POST "http://localhost:8001/api/v1/user-activities/" \
  -H "Content-Type: application/json" \
  -d '{"telegram_user_id": 123456789, "menu_item_id": 1, "activity_type": "navigation"}'
```

## 📚 API Документация

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## ⚠️ Статус эндпоинтов

**✅ Реализованы:**
- `GET /api/v1/menu-items/` - Меню
- `GET /api/v1/menu-items/{id}/content` - Контент
- `POST /api/v1/user-activities/` - Активность
- `POST /api/v1/webhook/telegram` - Webhook

**❌ Остальные заглушки:**

## 🔧 Разработка

### Добавление эндпоинта

1. Модель в `models/`
2. CRUD в `crud/`
3. Схемы в `schemas/`
4. Эндпоинт в `api/v1/`
5. Роутер в `api/routers.py`

### Форматирование

```bash
poetry run black backend/
poetry run isort backend/
poetry run flake8 backend/
```
