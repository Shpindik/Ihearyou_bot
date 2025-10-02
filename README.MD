# IHearYou Bot — монорепозиторий

Репозиторий включает три взаимосвязанных компонента:

- `backend/` — FastAPI-сервис админки (см. [backend/README.md](backend/README.md)).
- `bot/` — Telegram-бот на aiogram (см. [bot/README.md](bot/README.md)).
- `frontend/` — React/Vite SPA для администраторов (см. [frontend/README.md](frontend/README.md)).

## Архитектура

```
Telegram <-> bot (aiogram)
          │
          │ REST
          ▼
      backend (FastAPI) <---- frontend (React)
          │
          ├── Postgres (данные)
          └── Redis (кэш, брокер Celery)

Celery worker (фоновые уведомления пользователям)
```

- Бот принимает сообщения пользователей и сохраняет их данные в Postgres.
- Backend предоставляет REST API для авторизации администраторов и просмотра пользователей.
- Frontend обращается к backend за токенами и данными, отображает список пользователей и их аватары.

## Требования

- Docker & Docker Compose (для быстрого запуска).
- Python 3.10+ и Node 18+ (если запускать компоненты отдельно).
- Postgres 13+ (локально или через docker-compose).
 - Redis 7+ (поднимется из compose).

## Переменные окружения

Перечень ключевых переменных приведён в README отдельных компонентов. Основные:

- `BOT_TOKEN` — токен Telegram-бота (используется ботом и backend'ом для аватаров).
- `POSTGRES_*`, `DB_*` — параметры подключения к базе.
- `ADMIN_*` — настройки административного API (секрет, токен, логин/пароль).
- `REDIS_URL` — строка подключения к Redis (например, `redis://redis:6379/0`).

Создайте файл `.env` в корне (пример):

```
# Database Configuration
POSTGRES_DB=ihearyou_db
POSTGRES_USER=postgres_user
POSTGRES_PASSWORD=postgres_password
DB_HOST=db
DB_PORT=5432

# База данных
DATABASE_URL=postgresql+asyncpg://postgres_user:postgres_password@db:5432/ihearyou_db

# Redis
REDIS_URL=redis://redis:6379/0


# Bot Configuration
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN(Получем у Bot-Father)

# Admin Configuration
ADMIN_SECRET_KEY=changeme_secret_key_please_change_in_production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin12345

# API Configuration
BOT_API_PORT=8001

# Frontend Configuration
FRONTEND_API_URL=http://localhost:8001/api
FRONTEND_PORT=3001

# JWT настройки
JWT_SECRET_KEY=your_secret_key_here
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=60
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7
```

## Быстрый старт через Docker Compose

```bash
docker-compose up --build -d
```

- Backend: `http://localhost:8001`
- Frontend: `http://localhost:3001`
- Redis и Celery-воркер стартуют автоматически; бот работает в режиме polling.

Для live-пересборки используйте `docker-compose up --watch`.


### Загрузка flow-данных (меню)

```bash
docker-compose run --rm bot_api python backend/load_flow_data.py
```

После загрузки flow бэкенд очищает кэш меню в Redis.

## Кэширование и фоновые задания

- Кэш меню/контента хранится в Redis (TTL 300 сек). Ключи:
  - `menu_items:{telegram_user_id}:{parent_id|root}`
  - `menu_content:{telegram_user_id}:{menu_id}`
- При изменении flow кэш инвалидацируется по префиксам.
- Уведомления об ответе на вопрос отправляются пользователю через Celery-задачу `backend.tasks.send_telegram_message` (брокер Redis).


Убедитесь, что переменные окружения настроены верно.

## Полезные ссылки

- [Backend README](backend/README.md)
- [Bot README](bot/README.md)
- [Frontend README](frontend/README.md)
