.PHONY: help build up down logs shell-backend shell-db migrate makemigrations test lint format

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ── Docker ────────────────────────────────────────────────────────────────────
build: ## Build all Docker images
	docker compose build

up: ## Start all services
	docker compose up -d

down: ## Stop all services
	docker compose down

logs: ## Tail logs for all services
	docker compose logs -f

logs-backend: ## Tail backend logs
	docker compose logs -f backend

logs-celery: ## Tail celery logs
	docker compose logs -f celery

# ── Django ────────────────────────────────────────────────────────────────────
shell-backend: ## Open a shell in the backend container
	docker compose exec backend bash

shell-db: ## Open a MySQL shell
	docker compose exec db mysql -u $${MYSQL_USER} -p$${MYSQL_PASSWORD} $${MYSQL_DATABASE}

migrate: ## Run Django migrations
	docker compose exec backend python manage.py migrate

makemigrations: ## Create new Django migrations
	docker compose exec backend python manage.py makemigrations

createsuperuser: ## Create a Django superuser
	docker compose exec backend python manage.py createsuperuser

collectstatic: ## Collect static files
	docker compose exec backend python manage.py collectstatic --noinput

# ── Testing ───────────────────────────────────────────────────────────────────
test: ## Run backend tests
	docker compose exec backend pytest tests/ -v

test-coverage: ## Run tests with coverage report
	docker compose exec backend pytest tests/ --cov=apps --cov-report=html --cov-report=term-missing

# ── Code quality ──────────────────────────────────────────────────────────────
lint-backend: ## Lint backend with flake8
	docker compose exec backend flake8 apps/ --max-line-length=120

lint-frontend: ## Lint frontend
	docker compose run --rm frontend npm run lint

type-check: ## TypeScript type check
	docker compose run --rm frontend npm run type-check

# ── Local dev (without Docker) ────────────────────────────────────────────────
dev-backend: ## Run backend locally (requires venv)
	cd backend && DJANGO_SETTINGS_MODULE=config.settings.development python manage.py runserver

dev-frontend: ## Run frontend locally
	cd frontend && npm run dev

install-backend: ## Install backend dependencies
	cd backend && pip install -r requirements.txt

install-frontend: ## Install frontend dependencies
	cd frontend && npm ci
