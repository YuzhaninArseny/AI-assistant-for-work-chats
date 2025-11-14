# syntax=docker/dockerfile:1.7-labs
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONPATH="/app/saver/src:/app/shared/src"

WORKDIR /app

# ---- базовые утилиты (по минимуму) ----

# ---- Poetry + кэш pip/poetry ----
RUN --mount=type=cache,id=pip-cache,target=/root/.cache/pip \
    pip install "poetry==2.2.1"

# ---- манифесты для кэшируемого резолва ----
# shared
COPY shared/pyproject.toml /app/shared/pyproject.toml
# (если есть) lock
COPY shared/poetry.lock     /app/shared/poetry.lock
# saver
COPY saver/pyproject.toml /app/saver/pyproject.toml
# (если есть) lock
COPY saver/poetry.lock     /app/saver/poetry.lock

# ---- предварительная установка зависимостей без исходников ----
# Важно: в saver зависимость на shared должна быть вида:
#   shared = { path = "../shared", develop = true }
# Тогда ниже создастся editable-ссылка на /app/shared
RUN --mount=type=cache,id=poetry-cache,target=/root/.cache/pypoetry \
    poetry -C /app/saver install --with dev --no-root --sync

# ---- копируем исходники (перезапишутся томами в dev) ----
COPY shared/src /app/shared/src
COPY saver/src /app/saver/src

# Финальный прогон, чтобы гарантированно создать editable links
RUN --mount=type=cache,id=poetry-cache,target=/root/.cache/pypoetry \
    poetry -C /app/saver install --with dev --sync

# uvicorn попадёт в .venv (если указан в deps dev/main)
ENV PATH="/app/saver/.venv/bin:$PATH"
WORKDIR /app/saver

# dev: авто-перезапуск и watch src обоих модулей
# Добавь --reload-dir для shared, чтобы ловить изменения и там.
CMD ["uvicorn", "saver_app.main:app", \
     "--host", "0.0.0.0", "--port", "8000", \
     "--reload", "--reload-dir", "/app/saver/src", \
     "--reload-dir", "/app/shared/src"]