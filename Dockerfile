# syntax=docker/dockerfile:1.7
FROM python:3.11-slim

# системные настройки окружения (см. пояснения ниже)
ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.2.1

# базовые системные утилиты
#RUN apt-get update && apt-get install -y --no-install-recommends build-essential curl \
#    && rm -rf /var/lib/apt/lists/*

# ставим poetry
RUN pip install "poetry==${POETRY_VERSION}"

WORKDIR /app

# важно: сначала копируем «манифесты», чтобы кэш слоёв сохранялся
COPY pyproject.toml poetry.lock* ./

# не создаём venv внутри контейнера, ставим в системный site-packages (быстрее/проще)
RUN poetry config virtualenvs.create false

# кэшируем скачивание зависимостей между билдами (BuildKit)
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --with dev --no-interaction --no-ansi

# код копировать не будем — в деве смонтируем томом (hot-reload)
# если хочешь без тома — раскомментируй:
# COPY ./app /app

# команда запуска (FastAPI через uvicorn; --reload удобен для дев-режима)
WORKDIR /app
ENV PYTHONPATH=/app
# ебался с этой хуетой очень долго, проблемы с импортами etc. тут надо нрм фундамент и понимания докера, я застрял
CMD ["uvicorn","src.main:app","--host","0.0.0.0","--port","8000","--reload"]


