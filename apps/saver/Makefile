# ===== Docker Compose shortcuts =====
# Подсказка по целям: make help

COMPOSE := docker compose
DB_C := tgchats_db
APP_C := tgchats_app

.PHONY: help up up-build build ps logs db-logs app-logs db-ready db-psql db-sh app-sh restart down down-v

help: ## Показать все команды
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS=":.*?## "}; {printf "\033[36m%-14s\033[0m %s\n", $$1, $$2}'

up: ## Поднять ВСЕ сервисы в фоне
	$(COMPOSE) up -d

up-build: ## Пересобрать образы и поднять сервисы
	$(COMPOSE) up -d --build

build: ## Только пересобрать образы
	$(COMPOSE) build

ps: ## Статус контейнеров
	$(COMPOSE) ps

logs: ## Логи всех сервисов (стрим)
	$(COMPOSE) logs -f

db-logs: ## Логи БД (стрим)
	$(COMPOSE) logs -f db

app-logs: ## Логи приложения (стрим)
	$(COMPOSE) logs -f app

db-ready: ## Проверить готовность Postgres (pg_isready)
	docker exec -it $(DB_C) pg_isready -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"

db-psql: ## Зайти в psql внутри контейнера БД
	docker exec -it $(DB_C) psql -U "$$POSTGRES_USER" -d "$$POSTGRES_DB"

db-sh: ## Шелл в контейнер БД
	-docker exec -it $(DB_C) bash || docker exec -it $(DB_C) sh

app-sh: ## Шелл в контейнер приложения
	-docker exec -it $(APP_C) bash || docker exec -it $(APP_C) sh

restart: ## Перезапустить только приложение
	$(COMPOSE) restart app

down: ## Остановить все (ДАННЫЕ БД останутся)
	$(COMPOSE) down

down-v: ## Остановить все и УДАЛИТЬ ДАННЫЕ БД (volume)
	$(COMPOSE) down -v
