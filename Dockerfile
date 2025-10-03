# syntax=docker/dockerfile:1.7
FROM python:3.11-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    POETRY_VERSION=2.2.1

WORKDIR /app

RUN pip install "poetry==${POETRY_VERSION}" && poetry --version

#зависимости
COPY pyproject.toml poetry.lock* ./
RUN poetry config virtualenvs.create false
RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --no-interaction --no-ansi

COPY . /app

# 4) чтобы импорты были «как локально»
ENV PYTHONPATH=/app

# 5) команда запуска (без --reload; для дев-режима зададим в compose)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
