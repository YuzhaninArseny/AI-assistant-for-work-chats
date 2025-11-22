FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONPATH="/app/summarization/src"

WORKDIR /app

RUN --mount=type=cache,id=pip-cache,target=/root/.cache/pip \
    pip install "poetry==2.2.1"

ENV PATH="/app/command_service/.venv/bin:$PATH"

WORKDIR /app/summarization

COPY summarization/src /app/summarization/src

CMD ["uvicorn", "summarization.api:app", \
     "--host", "0.0.0.0", "--port", "8001", \
     "--reload", "--reload-dir", "/app/summarization/src"]