FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/command_service/src:/app/shared/src"

WORKDIR /app
RUN pip install "poetry==2.2.1"


COPY shared/pyproject.toml /app/shared/pyproject.toml
COPY shared/poetry.lock     /app/shared/poetry.lock
COPY command_service/pyproject.toml /app/command_service/pyproject.toml
COPY command_service/poetry.lock     /app/command_service/poetry.lock


RUN poetry -C /app/command_service install --no-root --sync

COPY shared/src /app/shared/src
COPY command_service/src /app/command_service/src


WORKDIR /app/command_service

CMD ["poetry", "run", "uvicorn", "command_service_app.main:app", \
    "--host", "0.0.0.0", "--port", "8001"]
