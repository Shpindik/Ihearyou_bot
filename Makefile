# Makefile для проекта IHearYou Bot
# Команды для удобной разработки

.PHONY: help install build up down restart logs shell clean test format lint migrate migrate-create load-data

# Переменные
COMPOSE_FILE = docker-compose.yml
COMPOSE_STAGE_FILE = docker-compose.stage.yml
BOT_CONTAINER = bot
API_CONTAINER = bot_api
DB_CONTAINER = db

# Цвета для вывода
GREEN = \033[0;32m
YELLOW = \033[1;33m
RED = \033[0;31m
NC = \033[0m # No Color

# Динамическая проверка готовности сервисов
define wait-for-ready
	@echo "$(YELLOW)⏳ Ожидание готовности сервисов...$(NC)"
	@for i in $$(seq 1 20); do \
		if curl -s http://localhost:8001/health | grep -q "healthy"; then \
			echo "$(GREEN)✅ Сервисы готовы!$(NC)"; \
			exit 0; \
		fi; \
		echo "Попытка $$i/20 - ждем..."; \
		sleep 3; \
	done; \
	echo "$(RED)❌ Сервисы не готовы за 60 секунд!$(NC)"; \
	exit 1
endef

# Помощь
help: ## Показать справку по командам
	@echo "$(GREEN)IHearYou Bot - Команды для разработки$(NC)"
	@echo ""
	@echo "$(YELLOW)Основные команды:$(NC)"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(NC) %s\n", $$1, $$2}'

# =============================================================================
# POETRY И ЗАВИСИМОСТИ
# =============================================================================

poetry-install: ## Установить Poetry
	@echo "$(GREEN)Установка Poetry...$(NC)"
	pip install poetry==1.7.1

poetry-reinstall: ## Переустановить Poetry
	@echo "$(GREEN)Переустановка Poetry...$(NC)"
	pip uninstall poetry -y
	pip install poetry==1.7.1

poetry-config: ## Настроить Poetry
	@echo "$(GREEN)Настройка Poetry...$(NC)"
	poetry config virtualenvs.in-project true

poetry-lock: ## Обновить lock файл (с обновлением версий)
	@echo "$(GREEN)Обновление lock файла с обновлением версий...$(NC)"
	poetry lock

poetry-lock-no-update: ## Обновить lock файл без обновления версий
	@echo "$(GREEN)Обновление lock файла без обновления версий...$(NC)"
	poetry lock --no-update

poetry-update: ## Обновить зависимости
	@echo "$(GREEN)Обновление зависимостей...$(NC)"
	poetry update

poetry-show: ## Показать установленные пакеты
	@echo "$(GREEN)Установленные пакеты:$(NC)"
	poetry show

poetry-export: ## Экспортировать зависимости в requirements.txt
	@echo "$(GREEN)Экспорт зависимостей...$(NC)"
	poetry export -f requirements.txt --output requirements.txt --without-hashes

poetry-shell: ## Открыть shell в виртуальном окружении
	@echo "$(GREEN)Открытие shell в виртуальном окружении...$(NC)"
	poetry shell

# =============================================================================
# УСТАНОВКА И НАСТРОЙКА
# =============================================================================

install: ## Установить зависимости через Poetry
	@echo "$(GREEN)Установка зависимостей...$(NC)"
	poetry install

install-dev: ## Установить зависимости для разработки
	@echo "$(GREEN)Установка зависимостей для разработки...$(NC)"
	poetry install --with dev

install-prod: ## Установить только продакшн зависимости
	@echo "$(GREEN)Установка продакшн зависимостей...$(NC)"
	poetry install --only=main

# =============================================================================
# ДОБАВЛЕНИЕ ЗАВИСИМОСТЕЙ
# =============================================================================

add-main: ## Добавить зависимость в main (использование: make add-main PACKAGE=requests)
	@echo "$(GREEN)Добавление зависимости в main: $(PACKAGE)$(NC)"
	poetry add $(PACKAGE)

add-dev: ## Добавить зависимость в dev (использование: make add-dev PACKAGE=pytest)
	@echo "$(GREEN)Добавление зависимости в dev: $(PACKAGE)$(NC)"
	poetry add --group dev $(PACKAGE)

remove-package: ## Удалить зависимость (использование: make remove-package PACKAGE=requests)
	@echo "$(GREEN)Удаление зависимости: $(PACKAGE)$(NC)"
	poetry remove $(PACKAGE)

# =============================================================================
# ВЫПОЛНЕНИЕ КОМАНД В ВИРТУАЛЬНОМ ОКРУЖЕНИИ
# =============================================================================

run-uvicorn: ## Запустить uvicorn в виртуальном окружении
	@echo "$(GREEN)Запуск uvicorn...$(NC)"
	poetry run uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

run-bot: ## Запустить бота в виртуальном окружении
	@echo "$(GREEN)Запуск бота...$(NC)"
	poetry run python bot/main.py

run-tests: ## Запустить тесты в виртуальном окружении
	@echo "$(GREEN)Запуск тестов...$(NC)"
	poetry run pytest

run-tests-coverage: ## Запустить тесты с покрытием в виртуальном окружении
	@echo "$(GREEN)Запуск тестов с покрытием...$(NC)"
	poetry run pytest --cov=backend --cov=bot

run-lint: ## Запустить линтер в виртуальном окружении
	@echo "$(GREEN)Запуск линтера...$(NC)"
	poetry run ruff check backend/ bot/

run-lint-fix: ## Исправить ошибки линтера в виртуальном окружении
	@echo "$(GREEN)Исправление ошибок линтера...$(NC)"
	poetry run ruff check --fix backend/ bot/

run-format: ## Запустить форматирование в виртуальном окружении
	@echo "$(GREEN)Форматирование кода...$(NC)"
	poetry run ruff format backend/ bot/

run-alembic: ## Запустить alembic в виртуальном окружении (использование: make run-alembic COMMAND=upgrade head)
	@echo "$(GREEN)Запуск alembic: $(COMMAND)$(NC)"
	poetry run alembic $(COMMAND)

# =============================================================================
# DOCKER КОМАНДЫ
# =============================================================================

build: ## Собрать все контейнеры
	@echo "$(GREEN)Сборка контейнеров...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build

build-no-cache: ## Собрать контейнеры без кэша
	@echo "$(GREEN)Сборка контейнеров без кэша...$(NC)"
	docker-compose -f $(COMPOSE_FILE) build --no-cache

up: ## Запустить все сервисы
	@echo "$(GREEN)Запуск сервисов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d

up-build: ## Запустить сервисы с пересборкой
	@echo "$(GREEN)Запуск сервисов с пересборкой...$(NC)"
	docker-compose -f $(COMPOSE_FILE) up -d --build

down: ## Остановить все сервисы
	@echo "$(GREEN)Остановка сервисов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down

down-volumes: ## Остановить сервисы и удалить volumes
	@echo "$(GREEN)Остановка сервисов и удаление volumes...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down -v

restart: ## Перезапустить все сервисы
	@echo "$(GREEN)Перезапуск сервисов...$(NC)"
	docker-compose -f $(COMPOSE_FILE) restart

restart-api: ## Перезапустить только API
	@echo "$(GREEN)Перезапуск API...$(NC)"
	docker-compose -f $(COMPOSE_FILE) restart $(API_CONTAINER)

restart-bot: ## Перезапустить только бота
	@echo "$(GREEN)Перезапуск бота...$(NC)"
	docker-compose -f $(COMPOSE_FILE) restart $(BOT_CONTAINER)

restart-db: ## Перезапустить только базу данных
	@echo "$(GREEN)Перезапуск базы данных...$(NC)"
	docker-compose -f $(COMPOSE_FILE) restart $(DB_CONTAINER)

# =============================================================================
# ЛОГИ И МОНИТОРИНГ
# =============================================================================

logs: ## Показать логи всех сервисов
	docker-compose -f $(COMPOSE_FILE) logs -f

logs-api: ## Показать логи API
	docker-compose -f $(COMPOSE_FILE) logs -f $(API_CONTAINER)

logs-bot: ## Показать логи бота
	docker-compose -f $(COMPOSE_FILE) logs -f $(BOT_CONTAINER)

logs-db: ## Показать логи базы данных
	docker-compose -f $(COMPOSE_FILE) logs -f $(DB_CONTAINER)


status: ## Показать статус контейнеров
	@echo "$(GREEN)Статус контейнеров:$(NC)"
	docker-compose -f $(COMPOSE_FILE) ps
	@echo ""
	@echo "$(GREEN)Проверка доступности сервисов:$(NC)"
	@echo "Redis: $$(docker-compose -f $(COMPOSE_FILE) exec redis redis-cli ping 2>/dev/null || echo 'DOWN')"
	@echo "PostgreSQL: $$(docker-compose -f $(COMPOSE_FILE) exec db psql -U postgres -c 'SELECT 1' 2>/dev/null | grep -q '1 row' && echo 'UP' || echo 'DOWN')"
	@echo "API: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8001/health || echo 'DOWN')"

# =============================================================================
# РАБОТА С КОНТЕЙНЕРАМИ
# =============================================================================

shell-api: ## Подключиться к контейнеру API
	@echo "$(GREEN)Подключение к контейнеру API...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec $(API_CONTAINER) /bin/bash

shell-bot: ## Подключиться к контейнеру бота
	@echo "$(GREEN)Подключение к контейнеру бота...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec $(BOT_CONTAINER) /bin/bash

shell-db: ## Подключиться к контейнеру базы данных
	@echo "$(GREEN)Подключение к контейнеру базы данных...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec $(DB_CONTAINER) psql -U postgres -d ihearyou

# =============================================================================
# ALEMBIC МИГРАЦИИ
# =============================================================================

migrate: ## Применить все миграции
	@echo "$(GREEN)Применение миграций...$(NC)"
	$(call wait-for-ready)
	docker-compose -f $(COMPOSE_FILE) exec $(API_CONTAINER) alembic upgrade head

migrate-create: ## Создать новую миграцию (использование: make migrate-create MESSAGE="описание")
	@echo "$(GREEN)Создание миграции: $(MESSAGE)$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec $(API_CONTAINER) alembic revision --autogenerate -m "$(MESSAGE)"

migrate-history: ## Показать историю миграций
	@echo "$(GREEN)История миграций:$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec $(API_CONTAINER) alembic history

migrate-current: ## Показать текущую версию миграции
	@echo "$(GREEN)Текущая версия миграции:$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec $(API_CONTAINER) alembic current

migrate-downgrade: ## Откатить миграцию на один шаг
	@echo "$(GREEN)Откат миграции на один шаг...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec $(API_CONTAINER) alembic downgrade -1

migrate-reset: ## Сбросить все миграции (ОСТОРОЖНО!)
	@echo "$(RED)ВНИМАНИЕ: Это удалит все данные!$(NC)"
	@read -p "Вы уверены? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker-compose -f $(COMPOSE_FILE) exec $(API_CONTAINER) alembic downgrade base
	docker-compose -f $(COMPOSE_FILE) exec $(API_CONTAINER) alembic upgrade head

# =============================================================================
# ДАННЫЕ И ТЕСТИРОВАНИЕ
# =============================================================================

load-data: ## Загрузить тестовые данные
	@echo "$(GREEN)Загрузка тестовых данных...$(NC)"
	$(call wait-for-ready)
	docker-compose -f $(COMPOSE_FILE) exec $(API_CONTAINER) python backend/load_flow_data.py

db-backup: ## Создать бэкап базы данных
	@echo "$(GREEN)Создание бэкапа базы данных...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec $(DB_CONTAINER) pg_dump -U postgres ihearyou > backup_$(shell date +%Y%m%d_%H%M%S).sql

db-restore: ## Восстановить базу данных из бэкапа (использование: make db-restore FILE=backup.sql)
	@echo "$(GREEN)Восстановление базы данных из $(FILE)...$(NC)"
	docker-compose -f $(COMPOSE_FILE) exec -T $(DB_CONTAINER) psql -U postgres ihearyou < $(FILE)

# =============================================================================
# ОЧИСТКА
# =============================================================================

clean: ## Очистить неиспользуемые Docker ресурсы
	@echo "$(GREEN)Очистка Docker ресурсов...$(NC)"
	docker system prune -f

clean-all: ## Полная очистка Docker (включая volumes)
	@echo "$(RED)ВНИМАНИЕ: Это удалит все Docker данные!$(NC)"
	@read -p "Вы уверены? (y/N): " confirm && [ "$$confirm" = "y" ]
	docker system prune -af --volumes

clean-containers: ## Удалить все контейнеры проекта
	@echo "$(GREEN)Удаление контейнеров проекта...$(NC)"
	docker-compose -f $(COMPOSE_FILE) down --rmi all --volumes --remove-orphans

# =============================================================================
# РАЗВЕРТЫВАНИЕ
# =============================================================================

deploy-stage: ## Развернуть на staging
	@echo "$(GREEN)Развертывание на staging...$(NC)"
	docker-compose -f $(COMPOSE_STAGE_FILE) up -d --build

deploy-stage-down: ## Остановить staging
	@echo "$(GREEN)Остановка staging...$(NC)"
	docker-compose -f $(COMPOSE_STAGE_FILE) down

# =============================================================================
# УТИЛИТЫ
# =============================================================================

health-check: ## Проверить здоровье сервисов
	@echo "$(GREEN)Проверка здоровья сервисов...$(NC)"
	@echo "API Root: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8001/ || echo 'DOWN')"
	@echo "API Health: $$(curl -s -o /dev/null -w '%{http_code}' http://localhost:8001/health || echo 'DOWN')"
	@echo ""
	@echo "$(GREEN)Детальная информация API:$(NC)"
	@curl -s http://localhost:8001/health | python -m json.tool 2>/dev/null || echo "API недоступен"

env-check: ## Проверить переменные окружения
	@echo "$(GREEN)Проверка переменных окружения...$(NC)"
	@if [ -f .env ]; then \
		echo "✅ .env файл найден"; \
		echo "Переменные:"; \
		grep -v '^#' .env | grep -v '^$$' | sed 's/=.*/=***/' ; \
	else \
		echo "❌ .env файл не найден"; \
		echo "Скопируйте .env.example в .env и настройте переменные"; \
	fi

build-poetry: ## Полная настройка Poetry с нуля
	@echo "$(GREEN)Полная настройка Poetry...$(NC)"
	@make poetry-install
	@make poetry-config
	@make poetry-lock-no-update
	@make install-dev
	@echo "$(GREEN)Poetry настроен и готов к работе!$(NC)"

rebuild-poetry: ## Переустановка Poetry с venv
	@echo "$(GREEN)Переустановка Poetry...$(NC)"
	@echo "$(YELLOW)Удаление старого виртуального окружения...$(NC)"
	@if [ -d ".venv" ]; then \
		rm -rf .venv; \
		echo "$(GREEN)✅ Старое виртуальное окружение удалено$(NC)"; \
	else \
		echo "$(YELLOW)⚠️  Виртуальное окружение не найдено$(NC)"; \
	fi
	@make poetry-reinstall
	@make poetry-config
	@make poetry-lock-no-update
	@make install-dev
	@echo "$(GREEN)Poetry настроен и готов к работе!$(NC)"

setup: ## Первоначальная настройка проекта
	@echo "$(GREEN)🚀 Первоначальная настройка проекта IHearYou Bot...$(NC)"
	@echo ""
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Создание .env файла...$(NC)"; \
		cp .env.example .env; \
		echo "$(GREEN)✅ Создан .env файл из .env.example$(NC)"; \
		echo "$(YELLOW)⚠️  Не забудьте настроить переменные BOT_TOKEN в .env$(NC)"; \
	else \
		echo "$(GREEN)✅ .env файл уже существует$(NC)"; \
	fi
	@echo ""
	@echo "$(YELLOW)Настройка Poetry...$(NC)"
	@make build-poetry
	@echo ""
	@echo "$(YELLOW)Сборка и запуск контейнеров...$(NC)"
	@make build
	@make up
	$(call wait-for-ready)
	@echo ""
	@echo "$(YELLOW)Применение миграций и загрузка данных...$(NC)"
	@make migrate
	@make load-data
	@echo ""
	@echo "$(GREEN)🎉 Проект готов к работе!$(NC)"
	@echo "$(GREEN)🌐 API: http://localhost:8001$(NC)"
	@echo "$(GREEN)📖 API Docs: http://localhost:8001/docs$(NC)"
	@echo "$(GREEN)📋 Health Check: http://localhost:8001/health$(NC)"

# =============================================================================
# БЫСТРЫЕ КОМАНДЫ
# =============================================================================

dev: ## Быстрый старт для разработки
	@echo "$(GREEN)🚀 Запуск в режиме разработки...$(NC)"
	@echo "$(YELLOW)Сборка и запуск с ожиданием готовности API...$(NC)"
	@make up-build
	$(call wait-for-ready)
	@echo "$(YELLOW)Загрузка данных...$(NC)"
	@make migrate
	@make load-data
	@echo "$(GREEN)✅ Проект готов! Открывайте логи...$(NC)"
	@make logs

stop: ## Быстрая остановка
	@echo "$(GREEN)Остановка сервисов...$(NC)"
	@make down

quick-restart: ## Быстрый перезапуск (без сброса данных)
	@echo "$(GREEN)Быстрый перезапуск сервисов...$(NC)"
	@make restart
	$(call wait-for-ready)
	@echo "$(GREEN)✅ Сервисы перезапущены!$(NC)"

reload-api: ## Перезагрузить API
	@echo "$(GREEN)Перезагрузка API...$(NC)"
	@make down
	@make up-build
	$(call wait-for-ready)
	@echo "$(GREEN)✅ API перезагружен!$(NC)"

reset: ## Полный сброс и перезапуск проекта
	@echo "$(RED)ВНИМАНИЕ: Это удалит все данные!$(NC)"
	@read -p "Вы уверены? (y/N): " confirm && [ "$$confirm" = "y" ]
	@echo "$(YELLOW)Остановка и очистка...$(NC)"
	@make down-volumes
	@make clean-containers
	@echo "$(YELLOW)Пересборка образов...$(NC)"
	@make build-no-cache
	@echo "$(YELLOW)Запуск сервисов...$(NC)"
	@make up
	$(call wait-for-ready)
	@echo "$(YELLOW)Применение миграций...$(NC)"
	@make migrate
	@echo "$(YELLOW)Загрузка тестовых данных...$(NC)"
	@make load-data
	@echo ""
	@echo "$(GREEN)🎉 Проект сброшен и готов к работе!$(NC)"
	@echo "$(GREEN)🌐 API: http://localhost:8001$(NC)"
	@echo "$(GREEN)📖 Docs: http://localhost:8001/docs$(NC)"
