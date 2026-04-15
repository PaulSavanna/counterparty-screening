# Counterparty Screening Workflow

Full-stack application for deterministic counterparty screening. The repository combines a FastAPI backend, a React frontend, persisted check history, Alembic migrations, and CI checks around linting, tests, and production build output.

See `docs/signal-model.md` for the signal and scoring rules.

## Stack

- **Backend**: FastAPI, SQLAlchemy, Alembic, Pydantic, Uvicorn
- **Frontend**: React, Vite, ESLint, Vitest
- **Database**: SQLite for local development, PostgreSQL in Docker
- **Tooling**: Pytest, Ruff, GitHub Actions, Docker Compose

## Architecture

```text
frontend (React/Vite)
        |
        v
FastAPI API
  ├── routes         HTTP boundary
  ├── services       signal collection + scoring + summaries
  ├── repositories   persistence boundary
  └── models         stored check results
        |
        v
SQLite (local) / PostgreSQL (Docker)
```

## Repository layout

```text
.
├── app/
│   ├── api/
│   ├── core/
│   ├── db/
│   ├── models/
│   ├── repositories/
│   ├── schemas/
│   └── services/
├── docs/
├── frontend/
├── migrations/
├── tests/
├── Dockerfile
├── docker-compose.yml
├── Makefile
└── pyproject.toml
```

## Quick start

### Local development

Backend:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm install
npm run dev
```

Open:

- Frontend: `http://localhost:5173`
- API docs: `http://localhost:8000/docs`

### Docker

```bash
docker compose up --build
```

Open:

- Frontend: `http://localhost:8080`
- API docs: `http://localhost:8000/docs`

## Environment configuration

See `.env.example`.

Key variables:

- `DATABASE_URL`: SQLite by default for local development, PostgreSQL-ready for containerized environments
- `AUTO_MIGRATE_ON_STARTUP`: disabled by default; run `alembic upgrade head` explicitly in local development
- `RISK_MEDIUM_THRESHOLD`, `RISK_HIGH_THRESHOLD`, `MAX_RISK_SCORE`: scoring controls
- `CORS_ORIGINS`: comma-separated frontend origins

## API example

```bash
curl -X POST http://localhost:8000/api/v1/checks \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Northwind Supply BV",
    "tax_id": "NL12345678B01",
    "country": "NL"
  }'
```

Example response shape:

```json
{
  "id": 1,
  "company_name": "Northwind Supply BV",
  "tax_id": "NL12345678B01",
  "country": "NL",
  "risk_score": 20.0,
  "severity": "low",
  "summary": "...",
  "signals": [
    {
      "source": "registry",
      "title": "Recent corporate profile change indicator",
      "score": 16,
      "details": "..."
    }
  ],
  "created_at": "2026-04-15T12:00:00Z"
}
```

## Available commands

```bash
make install          # install backend and frontend dependencies
make migrate          # run Alembic migrations
make lint             # ruff + frontend eslint
make test             # backend tests with coverage
make frontend-test    # frontend unit tests
make build            # frontend production build
make docker-up        # run full Docker stack
```

## Notes on implementation

- the stored record keeps only the data required to reproduce the result view: company fields, score, summary, and the normalized signal payload
- risk scoring is source-aware: repeated signals from one source are discounted and cross-source agreement adds a small escalation bonus
- summaries are generated deterministically from the computed severity and signal set

## Quality gates

GitHub Actions runs:

- Ruff on the backend
- Pytest with coverage
- frontend ESLint
- frontend Vitest
- frontend production build
- Docker Compose smoke test
