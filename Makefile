.PHONY: up down build migrate seed test lint setup dev-up

# Production stack (Postgres + gunicorn + nginx). Fresh machine: make setup && make up
up:
	docker compose up -d --build

down:
	docker compose down

build:
	docker compose build

# Hot-reload stack (Vite + Django runserver)
dev-up:
	docker compose -f docker-compose.dev.yml up --build

migrate:
	cd backend && python manage.py migrate

setup:
	cp -n .env.example .env || true
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

seed:
	cd backend && python manage.py seed_demo

test:
	cd backend && pytest -v --cov=apps --cov-report=term-missing:skip-covered --cov-fail-under=70

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

dev-backend:
	cd backend && python manage.py runserver

dev-frontend:
	cd frontend && npm run dev
