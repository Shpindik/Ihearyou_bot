# Backend API - "Я тебя слышу"

## 📋 Обзор

FastAPI приложение для Telegram-бота поддержки родителей детей с нарушением слуха.

**Текущее состояние:** Полнофункциональная система с административной панелью, публичным API и интеграцией с Telegram Bot.

## Архитектура

Проект построен по принципам Clean Architecture с разделением на слои:

- **API Layer** (`api/`) — HTTP эндпоинты и маршрутизация
- **Service Layer** (`services/`) — бизнес-логика приложения  
- **CRUD Layer** (`crud/`) — операции с базой данных
- **Model Layer** (`models/`) — SQLAlchemy модели
- **Schema Layer** (`schemas/`) — Pydantic схемы для валидации
- **Core Layer** (`core/`) — конфигурация, безопасность, зависимости

## Поток данных

### Аутентификация администраторов
1. POST `/api/v1/admin/auth/login` с логином и паролем
2. Проверка учетных данных в базе данных
3. Создание JWT access/refresh токенов
4. Использование токенов в заголовке `Authorization: Bearer <TOKEN>`

### Работа с пользователями Telegram
1. Регистрация пользователей через Bot API (`/api/v1/bot/telegram-user/register`)
2. Публичные эндпоинты для работы с контентом (`/api/v1/public/*`)
3. Запись активности и аналитика

### Административные функции
1. Управление контентом через Admin API (`/api/v1/admin/*`)
2. Модерация вопросов пользователей
3. Аналитика и отчеты
4. Система уведомлений

## Переменные окружения

Создайте `.env` файл с необходимыми переменными:

```bash
# База данных (автоматически настроена в Docker)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@db:5432/ihearyou

# Redis (автоматически настроен в Docker)
REDIS_URL=redis://redis:6379/0

# JWT настройки
JWT_SECRET_KEY=your-secret-key-here

# Администратор по умолчанию
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin12345
ADMIN_EMAIL=admin@example.com

# Telegram Bot
BOT_TOKEN=your-telegram-bot-token

# API настройки
BOT_API_PORT=8001
ENVIRONMENT=development
DEBUG=false
LOG_LEVEL=INFO

# Email настройки (опционально)
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_FROM=noreply@yourapp.com
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587

# Webhook настройки (опционально)
WEBHOOK_URL=
WEBHOOK_SECRET=

# Настройки напоминаний
INACTIVE_DAYS_THRESHOLD=10
REMINDER_COOLDOWN_DAYS=10
API_TIMEOUT=30
API_MAX_RETRIES=3
```

## 📁 Структура проекта

```
backend/
├── api/                    # HTTP эндпоинты
│   ├── v1/
│   │   ├── admin/         # Административные эндпоинты (JWT)
│   │   ├── bot/           # Bot API эндпоинты
│   │   └── public/        # Публичные эндпоинты
│   └── routers.py         # Главный роутер
├── core/                   # Ядро приложения
│   ├── config.py          # Конфигурация
│   ├── db.py              # Настройка БД
│   ├── dependencies.py    # FastAPI зависимости
│   ├── security.py        # JWT и безопасность
│   └── exception_handlers.py # Обработка ошибок
├── crud/                   # CRUD операции с БД
│   ├── base.py            # Базовый CRUD класс
│   ├── admin_user.py      # CRUD администраторов
│   ├── telegram_user.py   # CRUD пользователей Telegram
│   ├── menu_item.py       # CRUD пунктов меню
│   ├── question.py        # CRUD вопросов
│   ├── analytics.py       # CRUD аналитики
│   └── ...                # Другие CRUD классы
├── models/                 # SQLAlchemy модели
│   ├── admin_user.py      # Модель администраторов
│   ├── telegram_user.py   # Модель пользователей Telegram
│   ├── menu_item.py       # Модель пунктов меню
│   ├── content_file.py    # Модель файлов контента
│   ├── question.py        # Модель вопросов
│   ├── notification.py     # Модель уведомлений
│   ├── user_activity.py   # Модель активности
│   ├── message_template.py # Модель шаблонов
│   └── enums.py           # Перечисления
├── schemas/                # Pydantic схемы
│   ├── admin/             # Схемы для админ API
│   ├── bot/               # Схемы для Bot API
│   └── public/            # Схемы для публичного API
├── services/               # Бизнес-логика
│   ├── admin_user.py      # Сервис администраторов
│   ├── telegram_user.py   # Сервис пользователей Telegram
│   ├── menu_item.py       # Сервис меню
│   ├── question.py        # Сервис вопросов
│   ├── analytics.py       # Сервис аналитики
│   └── ...                # Другие сервисы
├── validators/             # Валидаторы бизнес-логики
├── utils/                  # Утилиты
├── tests/                  # Тесты
├── alembic/               # Миграции БД
├── main.py                # Точка входа FastAPI
└── load_flow_data.py      # Загрузка тестовых данных
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

Создайте `.env` файл (см. раздел "Переменные окружения" ниже) или используйте готовый пример:

```bash
# Скопируйте пример конфигурации
cp .env.example .env

# Отредактируйте необходимые переменные
nano .env
```

### 3. Запуск

```bash
# Локально
poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# Или через Docker (рекомендуется)
docker-compose up -d

# Или через Makefile
make dev
```

## 📊 База данных

### Миграции

```bash
# Создание миграции
poetry run alembic revision --autogenerate -m "описание изменений"

# Применение миграций
poetry run alembic upgrade head

# Откат миграции
poetry run alembic downgrade -1
```

### Загрузка тестовых данных

```bash
# Через Docker
docker-compose run --rm bot_api python backend/load_flow_data.py

# Через Makefile (рекомендуется)
make load-data

# Локально
poetry run python backend/load_flow_data.py
```

## 🧪 Тестирование

### Запуск тестов

```bash
# Все тесты
poetry run pytest

# Тесты с покрытием
poetry run pytest --cov=backend --cov=bot

# Конкретный тест
poetry run pytest backend/tests/test_admin_management.py::TestAdminUserAPI::test_login_success

# Через Makefile
make run-tests
make run-tests-coverage
```

### Проверка работоспособности

```bash
# Health check
curl http://localhost:8001/health

# API документация
open http://localhost:8001/docs
```

## 📚 API Документация

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## 🔌 Реализованные эндпоинты

### Административные API (`/api/v1/admin/`)

**Аутентификация:**
- `POST /auth/login` — вход в систему
- `POST /auth/refresh` — обновление токена
- `GET /auth/me` — информация о текущем администраторе
- `POST /auth/password-reset` — восстановление пароля

**Управление администраторами:**
- `GET /admin-users/` — список администраторов
- `POST /admin-users/` — создание администратора
- `GET /admin-users/{id}` — информация об администраторе
- `PATCH /admin-users/{id}` — обновление администратора
- `PATCH /admin-users/{id}/password` — смена пароля

**Управление пользователями:**
- `GET /telegram-users/` — список пользователей Telegram
- `GET /telegram-users/{id}` — информация о пользователе

**Управление контентом:**
- `GET /menu-items/` — список пунктов меню
- `POST /menu-items/` — создание пункта меню
- `PATCH /menu-items/{id}` — обновление пункта меню
- `DELETE /menu-items/{id}` — удаление пункта меню
- `GET /menu-items/{id}/content-files` — файлы контента
- `POST /menu-items/{id}/content-files` — создание файла контента

**Модерация вопросов:**
- `GET /user-questions/` — список вопросов
- `PATCH /user-questions/{id}` — ответ на вопрос

**Аналитика:**
- `GET /analytics/` — комплексная аналитика системы

**Уведомления:**
- `POST /notifications/` — отправка уведомления
- `GET /notifications/` — статистика уведомлений
- `GET /notifications/statistics` — детальная статистика

**Шаблоны сообщений:**
- `GET /message-templates/` — список шаблонов
- `POST /message-templates/` — создание шаблона
- `PATCH /message-templates/{id}` — обновление шаблона
- `DELETE /message-templates/{id}` — удаление шаблона

### Bot API (`/api/v1/bot/`)

**Пользователи:**
- `POST /telegram-user/register` — регистрация пользователя
- `GET /telegram-user/inactive-users` — неактивные пользователи
- `POST /telegram-user/update-reminder-status` — обновление статуса напоминания

**Шаблоны:**
- `GET /message-template/active-template` — активный шаблон

### Публичные API (`/api/v1/public/`)

**Меню:**
- `GET /menu-items/` — структура меню
- `GET /menu-items/{id}/content` — контент пункта меню

**Поиск:**
- `GET /search/` — поиск по материалам

**Активность:**
- `POST /user-activities/` — запись активности

**Вопросы:**
- `POST /user-questions/` — создание вопроса

**Оценки:**
- `POST /ratings/` — оценка материала

## 🔧 Разработка

### Добавление нового эндпоинта

1. **Модель** в `models/` — SQLAlchemy модель
2. **CRUD** в `crud/` — операции с базой данных
3. **Схемы** в `schemas/` — Pydantic схемы для валидации
4. **Сервис** в `services/` — бизнес-логика
5. **Валидатор** в `validators/` — валидация бизнес-правил
6. **Эндпоинт** в `api/v1/` — HTTP обработчики
7. **Тесты** в `tests/` — unit и интеграционные тесты

### Форматирование кода

```bash
# Форматирование и линтинг (рекомендуется)
poetry run ruff check --fix backend/
poetry run ruff format backend/

# Через Makefile
make run-lint-fix
make run-format

# Pre-commit hooks (автоматически при коммите)
poetry run pre-commit install
poetry run pre-commit run --all-files
```

### Структура тестов

```bash
backend/tests/
├── conftest.py           # Фикстуры pytest с pytest-postgresql
├── fixtures.py           # Тестовые данные
├── test_admin_management.py    # Тесты админ API
├── test_analytics_reporting.py # Тесты аналитики
├── test_auth_admin.py          # Тесты аутентификации
├── test_bot_integration.py      # Тесты Bot API
├── test_public_api.py           # Тесты публичного API
└── ...                          # Другие тесты

# Конфигурация тестов в pytest.ini
# Используется pytest-postgresql для тестовой БД
```

## 📝 Примеры API запросов

### Аутентификация администратора

```bash
# Вход в систему
curl -X POST "http://localhost:8001/api/v1/admin/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login": "admin@example.com",
    "password": "admin12345"
  }'

# Ответ:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Работа с меню (публичный API)

```bash
# Получение структуры меню
curl "http://localhost:8001/api/v1/public/menu-items/?telegram_user_id=123456789"

# Получение контента пункта меню
curl "http://localhost:8001/api/v1/public/menu-items/1/content?telegram_user_id=123456789"

# Поиск по материалам
curl "http://localhost:8001/api/v1/public/search/?telegram_user_id=123456789&query=слух&limit=10"
```

### Создание вопроса пользователем

```bash
curl -X POST "http://localhost:8001/api/v1/public/user-questions/" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_user_id": 123456789,
    "question_text": "Как помочь ребенку с нарушением слуха?"
  }'
```

### Оценка материала

```bash
curl -X POST "http://localhost:8001/api/v1/public/ratings/" \
  -H "Content-Type: application/json" \
  -d '{
    "telegram_user_id": 123456789,
    "menu_item_id": 1,
    "rating": 5
  }'
```

### Административные операции (требуют JWT токен)

```bash
# Получение списка пользователей
curl -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "http://localhost:8001/api/v1/admin/telegram-users/"

# Получение аналитики
curl -H "Authorization: Bearer <ACCESS_TOKEN>" \
  "http://localhost:8001/api/v1/admin/analytics/?period=month"

# Создание пункта меню
curl -X POST "http://localhost:8001/api/v1/admin/menu-items/" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Новый раздел",
    "description": "Описание раздела",
    "access_level": "free",
    "item_type": "navigation"
  }'
```

### Bot API для интеграции с Telegram

```bash
# Регистрация пользователя от бота
curl -X POST "http://localhost:8001/api/v1/bot/telegram-user/register" \
  -H "Content-Type: application/json" \
  -d '{
    "update_id": 123456,
    "message": {
      "message_id": 1,
      "from": {
        "id": 123456789,
        "first_name": "Иван",
        "last_name": "Петров",
        "username": "ivan_petrov"
      },
      "text": "/start"
    }
  }'

# Получение неактивных пользователей для напоминаний
curl "http://localhost:8001/api/v1/bot/telegram-user/inactive-users?inactive_days=10&days_since_last_reminder=7"
```

## 🏗️ Модели данных

### Основные сущности

- **AdminUser** — администраторы системы (роли: admin, moderator)
- **TelegramUser** — пользователи Telegram бота
- **MenuItem** — пункты меню с иерархической структурой
- **ContentFile** — файлы контента (текст, медиа, ссылки)
- **UserQuestion** — вопросы пользователей
- **UserActivity** — активность пользователей (просмотры, поиск, оценки)
- **Notification** — уведомления пользователям
- **MessageTemplate** — шаблоны сообщений для автоматических напоминаний

### Типы контента

- `TEXT` — текстовый контент
- `PHOTO`, `VIDEO`, `DOCUMENT` — медиафайлы Telegram
- `YOUTUBE_URL`, `VK_URL` — внешние видео
- `EXTERNAL_URL` — любые HTTP ссылки
- `WEB_APP` — Telegram Web App

### Уровни доступа

- `FREE` — бесплатный контент
- `PREMIUM` — премиум контент

## 🐳 Docker и инфраструктура

### Сервисы в docker-compose.yml

- **db** — PostgreSQL 13 с health check
- **redis** — Redis 7-alpine для кэширования
- **bot_api** — FastAPI backend (порт 8001 → 8000)
- **bot** — Telegram Bot с интеграцией к API

### Автоматические процессы

- Автоматическое применение миграций при запуске API
- Health checks для всех сервисов
- Автоматический перезапуск контейнеров
- Hot reload в режиме разработки

### Команды Makefile

```bash
# Основные команды
make dev          # Быстрый старт для разработки
make setup        # Первоначальная настройка проекта
make up           # Запуск всех сервисов
make down         # Остановка сервисов
make logs         # Просмотр логов

# Работа с данными
make migrate      # Применить миграции
make load-data    # Загрузить тестовые данные
make db-backup    # Создать бэкап БД

# Разработка
make run-tests    # Запустить тесты
make run-lint     # Проверить код
make run-format   # Форматировать код
```

## 🔒 Безопасность

- JWT токены для аутентификации администраторов
- Хеширование паролей с помощью bcrypt
- Валидация всех входных данных через Pydantic
- Обработка ошибок с детальными сообщениями

## 📦 Технологический стек

### Основные зависимости (pyproject.toml)

**Backend (FastAPI):**
- `fastapi` — веб-фреймворк
- `uvicorn` — ASGI сервер
- `sqlalchemy` — ORM для работы с БД
- `alembic` — миграции БД
- `asyncpg` — асинхронный драйвер PostgreSQL
- `python-jose` — JWT токены
- `passlib` — хеширование паролей
- `email-validator` — валидация email
- `fastapi-mail` — отправка писем

**Bot (aiogram):**
- `aiogram` — Telegram Bot API
- `aiohttp` — HTTP клиент
- `httpx` — современный HTTP клиент
- `redis` — кэширование
- `apscheduler` — планировщик задач

**Инструменты разработки:**
- `ruff` — быстрый линтер и форматтер
- `pytest` — тестирование
- `pytest-postgresql` — тестовая БД
- `pre-commit` — хуки для Git
