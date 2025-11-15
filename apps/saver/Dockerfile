# syntax=docker/dockerfile:1.7-labs
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/saver/src:/app/shared/src"

WORKDIR /app

RUN pip install poetry==2.2.1

COPY shared/pyproject.toml /app/shared/pyproject.toml
COPY shared/poetry.lock     /app/shared/poetry.lock
COPY saver/pyproject.toml /app/saver/pyproject.toml
COPY saver/poetry.lock     /app/saver/poetry.lock

# Важно: в saver зависимость на shared должна быть вида:
#   shared = { path = "../shared", develop = true }
# Тогда ниже создастся editable-ссылка на /app/shared
RUN poetry -C /app/saver install --with dev --no-root --sync

COPY shared/src /app/shared/src
COPY saver/src /app/saver/src

WORKDIR /app/saver

CMD ["poetry", "run", "uvicorn", "saver_app.main:app", "--host", "0.0.0.0", "--port", "8000"]