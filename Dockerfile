# Multi-stage: compact runtime image, uv for fast dependency install.

# ---- Builder --------------------------------------------------------
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:0.5.0 /uv /usr/local/bin/uv

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-install-project --no-dev || uv sync --no-install-project --no-dev

COPY manage.py ./
COPY whiskers ./whiskers
COPY accounts ./accounts
COPY catalog ./catalog
COPY orders ./orders

RUN uv sync --frozen --no-dev || uv sync --no-dev

# ---- Runtime --------------------------------------------------------
FROM python:3.12-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends libpq5 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --system app && useradd --system --gid app --home /app app

WORKDIR /app

COPY --from=builder --chown=app:app /app /app

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    DJANGO_SETTINGS_MODULE=whiskers.settings

USER app

EXPOSE 8000

CMD ["gunicorn", "whiskers.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
