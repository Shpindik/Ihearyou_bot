# IHearYou Bot — монорепозиторий

Репозиторий включает три взаимосвязанных компонента:

- `backend/` — FastAPI-сервис админки (см. [backend/README.md](backend/README.md)).
- `bot/` — Telegram-бот на aiogram (см. [bot/README.md](bot/README.md)).
- `frontend/` — React/Vite SPA для администраторов (см. [frontend/README.md](frontend/README.md)).

## Архитектура

```
Telegram <-> bot (aiogram) ----> Postgres <---- backend (FastAPI) <---- frontend (React)
```

- Бот принимает сообщения пользователей и сохраняет их данные в Postgres.
- Backend предоставляет REST API для авторизации администраторов и просмотра пользователей.
- Frontend обращается к backend за токенами и данными, отображает список пользователей и их аватары.

## Требования

- Docker & Docker Compose (для быстрого запуска).
- Python 3.11+ и Node 18+ (если запускать компоненты отдельно).
- Postgres 13+ (локально или через docker-compose).

## Переменные окружения

Перечень ключевых переменных приведён в README отдельных компонентов. Основные:

- `BOT_TOKEN` — токен Telegram-бота (используется ботом и backend'ом для аватаров).
- `POSTGRES_*`, `DB_*` — параметры подключения к базе.
- `ADMIN_*` — настройки административного API (секрет, токен, логин/пароль).

Создайте файл `.env` в корне (пример):

```
# Database Configuration
POSTGRES_DB=ihearyou_db
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=postgres_password
DB_HOST=db
DB_PORT=5432

# Bot Configuration
BOT_TOKEN=<Используйте токен, полученный у botfather>

# Admin Configuration
ADMIN_SECRET_KEY=changeme_secret_key_please_change_in_production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin12345

# API Configuration
BOT_API_PORT=8001

# Frontend Configuration
FRONTEND_API_URL=http://localhost:8001/api
FRONTEND_PORT=3001
```

## Быстрый старт через Docker Compose

```bash
docker-compose up --build
```

- Backend поднимется на `http://localhost:8001`.
- Frontend будет доступен на `http://localhost:3001` (проксируется контейнером).
- Бот запустится в режиме polling внутри контейнера.

Используйте `docker-compose up --watch`, чтобы автоматически пересобирать компоненты при изменениях кода.


Убедитесь, что переменные окружения настроены верно.

## Полезные ссылки

- [Backend README](backend/README.md)
- [Bot README](bot/README.md)
- [Frontend README](frontend/README.md)
