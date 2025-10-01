# Backend API - "Я тебя слышу"

## 📋 Обзор

FastAPI-приложение для Telegram-бота поддержки родителей детей с нарушением слуха.

**Текущее состояние:** Основные публичные и административные эндпоинты реализованы, добавлены кэширование (Redis) и фоновая доставка уведомлений через Celery.

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
- `REDIS_URL` — строка подключения к Redis (например, `redis://redis:6379/0`).



## Примеры API-запросов

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

### Публичные

- Получить меню (1 уровень):
```bash
curl "http://localhost:8001/api/v1/menu-items?telegram_user_id=123456789"
```

- Получить контент пункта:
```bash
curl "http://localhost:8001/api/v1/menu-items/1/content?telegram_user_id=123456789"
```

- Записать активность:
```bash
curl -X POST "http://localhost:8001/api/v1/user-activities" \
  -H "Content-Type: application/json" \
  -d '{"telegram_user_id":123456789, "menu_item_id":1, "activity_type":"navigation"}'
```

- Оценить материал:
```bash
curl -X POST "http://localhost:8001/api/v1/ratings" \
  -H "Content-Type: application/json" \
  -d '{"telegram_user_id":123456789, "menu_item_id":42, "rating":5}'
```

- Создать вопрос пользователя:
```bash
curl -X POST "http://localhost:8001/api/v1/user-questions" \
  -H "Content-Type: application/json" \
  -d '{"telegram_user_id":123456789, "question_text":"Как выбрать аппарат?"}'
```

### Админ

- Получить список вопросов (JWT требуется):
```bash
curl -H "Authorization: Bearer <JWT>" \
  "http://localhost:8001/api/v1/admin/user-questions?page=1&limit=20&status=pending"
```

- Ответить на вопрос (JWT требуется):
```bash
curl -X PUT -H "Authorization: Bearer <JWT>" \
  -H "Content-Type: application/json" \
  -d '{"answer_text":"Спасибо за вопрос! ..."}' \
  "http://localhost:8001/api/v1/admin/user-questions/10"
```

## 📁 Структура

```
backend/
├── api/                    # HTTP-эндпоинты (v1/public, v1/admin, v1/bot)
├── core/                   # Конфигурация и утилиты (config, db, cache, celery_app)
├── crud/                   # Операции с БД
├── models/                 # SQLAlchemy модели
├── schemas/                # Pydantic схемы
├── services/               # Бизнес-логика (menu_item, user_activity, question, notification)
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

### Загрузка данных (flow)

```bash
# Загрузка структуры меню
docker-compose run --rm bot_api python backend/load_flow_data.py
```

## 🧪 Тестирование

### Проверка работоспособности

```bash
# Health check
curl http://localhost:8001/health
```

### Работающие эндпоинты (сводка)

- Публичные: `GET /api/v1/menu-items`, `GET /api/v1/menu-items/{id}/content`, `POST /api/v1/user-activities`, `POST /api/v1/ratings`, `POST /api/v1/user-questions`
- Админ: `GET /api/v1/admin/user-questions`, `PUT /api/v1/admin/user-questions/{id}`

## 📚 API Документация

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## ⚙️ Кэширование (Redis)

- Включается переменной `REDIS_URL`.
- Ключи:
  - `menu_items:{telegram_user_id}:{parent_id|root}` — список пунктов меню (TTL 300 сек)
  - `menu_content:{telegram_user_id}:{menu_id}` — контент пункта (TTL 300 сек)
- Инвалидация: выполняется в конце `backend/load_flow_data.py` (очистка по префиксам `menu_items:` и `menu_content:`).

## 📨 Уведомления (Celery)

- При ответе админа на вопрос ставится Celery-задача `backend.tasks.send_telegram_message`.
- Брокер и результат — Redis (`REDIS_URL`).
- Запуск worker: `docker compose up -d celery_worker`.

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
