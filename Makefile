PYTHON ?= python3
PIP ?= $(PYTHON) -m pip
NPM ?= npm

.PHONY: install install-backend install-frontend api frontend dev migrate lint test frontend-test build clean docker-up docker-down

install: install-backend install-frontend

install-backend:
	$(PIP) install -e ".[dev]"

install-frontend:
	cd frontend && $(NPM) ci

api:
	uvicorn app.main:app --reload

frontend:
	cd frontend && $(NPM) run dev

dev:
	@echo "Run 'make api' and 'make frontend' in separate terminals."

migrate:
	alembic upgrade head

lint:
	ruff check .
	cd frontend && $(NPM) run lint

test:
	pytest --cov=app --cov-report=term-missing

frontend-test:
	cd frontend && $(NPM) run test

build:
	cd frontend && $(NPM) run build

clean:
	rm -rf .pytest_cache .ruff_cache frontend/dist

docker-up:
	docker compose up --build

docker-down:
	docker compose down --remove-orphans
