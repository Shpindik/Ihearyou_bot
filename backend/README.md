# Backend

## Обзор
Сервис построен на FastAPI и реализует административное API для управления ботом. Основные задачи:
- аутентификация администраторов по OAuth2 с паролем;
- выдача токенов доступа и проверка их валидности;
- получение списка пользователей, сохранённых ботом в БД;
- проксирование аватаров Telegram через бэкенд.

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

