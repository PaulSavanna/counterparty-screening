FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/* \
    && addgroup --system appgroup \
    && adduser --system --ingroup appgroup --home /home/appuser appuser \
    && mkdir -p /app/data \
    && chown -R appuser:appgroup /app /home/appuser

COPY pyproject.toml README.md alembic.ini ./
COPY app ./app
COPY migrations ./migrations

RUN pip install --no-cache-dir .

USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
