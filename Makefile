.PHONY: up down build migrate seed test lint setup

up:
	docker compose up -d

down:
	docker compose down

build:
	docker compose build

migrate:
	cd backend && python manage.py migrate

setup:
	cp -n .env.example .env || true
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

seed:
	cd backend && python manage.py seed_demo

test:
	cd backend && pytest -v

lint:
	cd backend && ruff check .
	cd frontend && npm run lint

dev-backend:
	cd backend && python manage.py runserver

dev-frontend:
	cd frontend && npm run dev
