FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONPATH="/app/command_service/src:/app/shared/src"

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
# command_service
COPY command_service/pyproject.toml /app/command_service/pyproject.toml
# (если есть) lock
COPY command_service/poetry.lock     /app/command_service/poetry.lock

# ---- предварительная установка зависимостей без исходников ----
# Важно: в command_service зависимость на shared должна быть вида:
#   shared = { path = "../shared", develop = true }
# Тогда ниже создастся editable-ссылка на /app/shared
RUN --mount=type=cache,id=poetry-cache,target=/root/.cache/pypoetry \
    poetry -C /app/command_service install --with dev --no-root --sync

# ---- копируем исходники (перезапишутся томами в dev) ----
COPY shared/src /app/shared/src
COPY command_service/src /app/command_service/src

# Финальный прогон, чтобы гарантированно создать editable links
RUN --mount=type=cache,id=poetry-cache,target=/root/.cache/pypoetry \
    poetry -C /app/command_service install --with dev --sync

# uvicorn попадёт в .venv (если указан в deps dev/main)
ENV PATH="/app/command_service/.venv/bin:$PATH"
WORKDIR /app/command_service


# dev: авто-перезапуск и watch src обоих модулей
# Добавь --reload-dir для shared, чтобы ловить изменения и там.
CMD ["uvicorn", "command_service_app.main:app", \
     "--host", "0.0.0.0", "--port", "8001", \
     "--reload", "--reload-dir", "/app/command_service/src", \
     "--reload-dir", "/app/shared/src"]
