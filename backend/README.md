# Backend API - "Я тебя слышу"

## 📋 Обзор

FastAPI приложение для Telegram-бота поддержки родителей детей с нарушением слуха.

**Текущее состояние:** Базовая структура готова, большинство эндпоинтов не реализованы.

## Поток данных

### Публичные эндпоинты (без аутентификации)
1. Telegram-бот отправляет POST `/api/v1/telegram-user/register` с данными пользователя
2. `TelegramUserService` создает или обновляет пользователя в БД через UPSERT
3. Пользователь получает меню через GET `/api/v1/menu-items/`
4. Активность пользователя записывается через POST `/api/v1/user-activities/`

### Административные эндпоинты (с JWT)
1. Администратор авторизуется через POST `/api/v1/admin/auth/login`
2. При успехе создаётся JWT-токен для доступа к админ-функциям
3. Защищённые эндпоинты проверяют токен через `HTTPBearer` dependency
4. Данные возвращаются через соответствующие сервисы и CRUD операции

## Переменные окружения

### База данных
- `DATABASE_URL` — строка подключения к PostgreSQL
- `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB`, `DB_HOST`, `DB_PORT` — компоненты подключения

### JWT аутентификация
- `JWT_SECRET_KEY` — секретный ключ для подписи JWT токенов
- `JWT_ALGORITHM` — алгоритм шифрования (по умолчанию HS256)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` — время жизни access токена (по умолчанию 60)
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS` — время жизни refresh токена (по умолчанию 7)

### Администратор по умолчанию
- `ADMIN_USERNAME` — имя пользователя администратора (по умолчанию admin)
- `ADMIN_PASSWORD` — пароль администратора (по умолчанию admin12345)
- `ADMIN_EMAIL` — email администратора (опционально)

### Telegram Bot
- `BOT_TOKEN` — токен Telegram-бота

### Логирование
- `LOG_LEVEL` — уровень логирования (по умолчанию INFO)

## 📁 Структура

```
backend/
├── api/                    # HTTP эндпоинты
│   ├── v1/                # API версии 1
│   │   ├── admin/         # Административные эндпоинты (JWT)
│   │   ├── bot/           # Bot API эндпоинты
│   │   └── public/        # Публичные эндпоинты
│   └── routers.py         # Централизованное подключение роутеров
├── core/                   # Конфигурация и утилиты
│   ├── config.py          # Настройки приложения
│   ├── db.py              # Подключение к БД
│   ├── exceptions.py      # Кастомные исключения
│   └── security.py        # JWT и безопасность
├── crud/                   # Операции с БД
│   ├── base.py            # Базовый CRUD класс
│   ├── content_file.py    # CRUD для файлов контента
│   ├── menu_item.py       # CRUD для пунктов меню
│   ├── telegram_user.py   # CRUD для пользователей Telegram
│   └── user_activity.py   # CRUD для активности пользователей
├── models/                 # SQLAlchemy модели
│   ├── admin_user.py      # Модель администраторов
│   ├── content_file.py    # Модель файлов контента
│   ├── enums.py           # Enum типы
│   ├── menu_item.py       # Модель пунктов меню
│   ├── notification.py    # Модель уведомлений
│   ├── question.py        # Модель вопросов
│   ├── reminder_template.py # Модель шаблонов напоминаний
│   ├── telegram_user.py   # Модель пользователей Telegram
│   └── user_activity.py   # Модель активности
├── schemas/                # Pydantic схемы
│   ├── admin/             # Схемы для админ API
│   ├── bot/               # Схемы для Bot API
│   └── public/            # Схемы для публичного API
├── services/               # Бизнес-логика
│   ├── admin_user.py      # Сервис администраторов
│   ├── content_file.py    # Сервис файлов контента
│   ├── menu_item.py       # Сервис пунктов меню
│   ├── notification.py    # Сервис уведомлений
│   ├── question.py        # Сервис вопросов
│   ├── reminder_template.py # Сервис шаблонов
│   ├── telegram_user.py   # Сервис пользователей Telegram
│   └── user_activity.py   # Сервис активности
├── validators/             # Валидаторы бизнес-логики
│   ├── admin_user.py      # Валидатор администраторов
│   ├── content_file.py    # Валидатор файлов контента
│   ├── menu_item.py       # Валидатор пунктов меню
│   ├── notification.py    # Валидатор уведомлений
│   ├── question.py        # Валидатор вопросов
│   ├── reminder_template.py # Валидатор шаблонов
│   ├── telegram_user.py   # Валидатор пользователей Telegram
│   └── user_activity.py   # Валидатор активности
├── alembic/               # Миграции БД
├── main.py                # Точка входа FastAPI
└── load_flow_data.py      # Загрузка тестовых данных
```

## 🚀 Быстрый старт

### 1. Установка Make

```bash
# Ubuntu/Debian
sudo apt update && sudo apt install make

# macOS (с Homebrew)
brew install make

# Windows (с Chocolatey)
choco install make

# Или через WSL
sudo apt install make
```

### 2. Первоначальная настройка

```bash
# Полная настройка проекта (создание .env, установка Poetry, сборка контейнеров)
make setup

# Или пошагово:
# 1. Создание .env файла
cp .env.example .env

# 2. Настройка Poetry
make build-poetry

# 3. Сборка и запуск контейнеров
make build
make up
```

### 3. Запуск в режиме разработки

```bash
# Быстрый старт для разработки
make dev

# Или пошагово:
make up-build
make migrate
make load-data
```

### 4. Проверка работоспособности

```bash
# Проверка здоровья сервисов
make health-check

# Просмотр логов
make logs

# Статус контейнеров
make status
```

## 📊 База данных

### Миграции

```bash
# Применение всех миграций
make migrate

# Создание новой миграции
make migrate-create MESSAGE="описание изменений"

# Просмотр истории миграций
make migrate-history

# Текущая версия
make migrate-current

# Откат на один шаг
make migrate-downgrade
```

### Загрузка данных

```bash
# Загрузка тестовых данных (структура меню)
make load-data

# Создание бэкапа
make db-backup

# Восстановление из бэкапа
make db-restore FILE=backup_20241201_120000.sql
```

## 🧪 Тестирование и разработка

### Локальная разработка

```bash
# Запуск API локально (в виртуальном окружении)
make run-uvicorn

# Запуск бота локально
make run-bot

# Запуск тестов
make run-tests

# Тесты с покрытием
make run-tests-coverage
```

### Качество кода

```bash
# Линтинг
make run-lint

# Автоисправление ошибок линтера
make run-lint-fix

# Форматирование кода
make run-format

# Или через Docker
make lint
make format
```

### Работа с Alembic

```bash
# Запуск alembic команд в виртуальном окружении
make run-alembic COMMAND=upgrade head
make run-alembic COMMAND=revision --autogenerate -m "новая миграция"
```

### Команды пересборки

```bash
# Переустановка Poetry с удалением старого venv
make rebuild-poetry

# Полная очистка и перезапуск проекта (удаляет все данные!)
make reset

# Очистка Docker ресурсов
make clean

# Полная очистка Docker (включая volumes) - ОСТОРОЖНО!
make clean-all

# Удаление всех контейнеров проекта
make clean-containers

# Быстрая остановка сервисов
make stop
```


## 📚 API Документация

- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc
- **API Health**: http://localhost:8001/health/api
- **DB Health**: http://localhost:8001/health/db

## ⚠️ Статус эндпоинтов

**✅ Реализованы:**
- `GET /api/v1/menu-items/` - Получение структуры меню
- `GET /api/v1/menu-items/{id}/content` - Получение контента пункта меню
- `POST /api/v1/user-activities/` - Запись активности пользователя
- `POST /api/v1/telegram-user/register` - Регистрация пользователя Telegram

**🔄 Частично реализованы:**
- Административные эндпоинты (структура готова, логика в разработке)
- Поиск по материалам (схемы готовы)
- Система оценок (схемы готовы)
- Вопросы пользователей (схемы готовы)

**❌ Заглушки:**
- Аутентификация администраторов
- Управление уведомлениями
- Аналитика
- Шаблоны напоминаний

## 🔧 Разработка

### Архитектура

Проект следует принципам Clean Architecture:

1. **Модели** (`models/`) - SQLAlchemy модели данных
2. **CRUD** (`crud/`) - Базовые операции с БД
3. **Схемы** (`schemas/`) - Pydantic модели для валидации
4. **Валидаторы** (`validators/`) - Бизнес-логика валидации
5. **Сервисы** (`services/`) - Сложная бизнес-логика
6. **API** (`api/`) - HTTP эндпоинты

### Добавление эндпоинта

1. Модель в `models/`
2. CRUD в `crud/`
3. Схемы в `schemas/`
4. Валидатор в `validators/`
5. Сервис в `services/`
6. Эндпоинт в `api/v1/`
7. Роутер в `api/routers.py`

### Make команды

#### Помощь
| Команда | Описание |
|---------|----------|
| `make help` | Показать справку по всем командам |

#### Poetry и зависимости
| Команда | Описание |
|---------|----------|
| `make poetry-install` | Установить Poetry версии 1.7.1 |
| `make poetry-reinstall` | Переустановить Poetry (удаляет старую версию) |
| `make poetry-config` | Настроить Poetry (включая virtualenvs.in-project) |
| `make poetry-lock` | Обновить lock файл с обновлением версий зависимостей |
| `make poetry-lock-no-update` | Обновить lock файл без обновления версий |
| `make poetry-update` | Обновить все зависимости до последних версий |
| `make poetry-show` | Показать установленные пакеты |
| `make poetry-export` | Экспортировать зависимости в requirements.txt |
| `make poetry-shell` | Открыть shell в виртуальном окружении |

#### Установка и настройка
| Команда | Описание |
|---------|----------|
| `make install` | Установить зависимости через Poetry |
| `make install-dev` | Установить зависимости для разработки (включая dev) |
| `make install-prod` | Установить только продакшн зависимости |

#### Добавление зависимостей
| Команда | Описание |
|---------|----------|
| `make add-main PACKAGE=requests` | Добавить зависимость в main группу |
| `make add-dev PACKAGE=pytest` | Добавить зависимость в dev группу |
| `make remove-package PACKAGE=requests` | Удалить зависимость |

#### Выполнение команд в виртуальном окружении
| Команда | Описание |
|---------|----------|
| `make run-uvicorn` | Запустить uvicorn локально (порт 8000, reload) |
| `make run-bot` | Запустить бота локально |
| `make run-tests` | Запустить тесты через pytest |
| `make run-tests-coverage` | Запустить тесты с покрытием кода |
| `make run-lint` | Запустить линтер (ruff) для backend/ и bot/ |
| `make run-lint-fix` | Исправить ошибки линтера автоматически |
| `make run-format` | Форматировать код (ruff format) |
| `make run-alembic COMMAND=upgrade head` | Запустить alembic команды |

#### Docker команды
| Команда | Описание |
|---------|----------|
| `make build` | Собрать все контейнеры |
| `make build-no-cache` | Собрать контейнеры без кэша |
| `make up` | Запустить все сервисы в фоне |
| `make up-build` | Запустить сервисы с пересборкой |
| `make down` | Остановить все сервисы |
| `make down-volumes` | Остановить сервисы и удалить volumes |
| `make restart` | Перезапустить все сервисы |
| `make restart-api` | Перезапустить только API контейнер |
| `make restart-bot` | Перезапустить только Bot контейнер |
| `make restart-db` | Перезапустить только базу данных |

#### Логи и мониторинг
| Команда | Описание |
|---------|----------|
| `make logs` | Показать логи всех сервисов (follow) |
| `make logs-api` | Показать логи API контейнера |
| `make logs-bot` | Показать логи Bot контейнера |
| `make logs-db` | Показать логи базы данных |
| `make logs-frontend` | Показать логи фронтенда |
| `make status` | Показать статус всех контейнеров |

#### Работа с контейнерами
| Команда | Описание |
|---------|----------|
| `make shell-api` | Подключиться к контейнеру API (bash) |
| `make shell-bot` | Подключиться к контейнеру Bot (bash) |
| `make shell-db` | Подключиться к базе данных (psql) |

#### Alembic миграции
| Команда | Описание |
|---------|----------|
| `make migrate` | Применить все миграции (ждет готовности API) |
| `make migrate-create MESSAGE="описание"` | Создать новую миграцию с автогенерацией |
| `make migrate-history` | Показать историю миграций |
| `make migrate-current` | Показать текущую версию миграции |
| `make migrate-downgrade` | Откатить миграцию на один шаг |
| `make migrate-reset` | Сбросить все миграции (ОСТОРОЖНО! удаляет данные) |

#### Данные и тестирование
| Команда | Описание |
|---------|----------|
| `make load-data` | Загрузить тестовые данные (ждет готовности API) |
| `make db-backup` | Создать бэкап базы данных с timestamp |
| `make db-restore FILE=backup.sql` | Восстановить базу данных из файла |

#### Очистка
| Команда | Описание |
|---------|----------|
| `make clean` | Очистить неиспользуемые Docker ресурсы |
| `make clean-all` | Полная очистка Docker (включая volumes) - ОСТОРОЖНО! |
| `make clean-containers` | Удалить все контейнеры проекта с volumes |

#### Развертывание
| Команда | Описание |
|---------|----------|
| `make deploy-stage` | Развернуть на staging окружении |
| `make deploy-stage-down` | Остановить staging окружение |

#### Утилиты
| Команда | Описание |
|---------|----------|
| `make health-check` | Проверить здоровье всех сервисов (HTTP коды) |
| `make env-check` | Проверить переменные окружения (.env файл) |
| `make build-poetry` | Полная настройка Poetry с нуля (install + config + lock + install-dev) |
| `make rebuild-poetry` | Переустановка Poetry с удалением .venv |

#### Быстрые команды
| Команда | Описание |
|---------|----------|
| `make setup` | Первоначальная настройка проекта (env + poetry + build + up + migrate) |
| `make dev` | Быстрый старт для разработки (up-build + wait + migrate + logs) |
| `make stop` | Быстрая остановка (alias для down) |
| `make reset` | Полный сброс проекта (удаляет все данные! down-volumes + clean + rebuild) |
