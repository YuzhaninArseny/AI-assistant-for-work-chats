FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONPATH="/app/response_draft_generator/src"

WORKDIR /app

RUN --mount=type=cache,id=pip-cache,target=/root/.cache/pip \
    pip install "poetry==2.2.1"

ENV PATH="/app/response_draft_generator/.venv/bin:$PATH"

WORKDIR /app/responce_draft_generator

COPY responce_draft_generator/src /app/responce_draft_generator/src

CMD ["uvicorn", "response_draft_generator.api:app", \
     "--host", "0.0.0.0", "--port", "8001", \
     "--reload", "--reload-dir", "/app/response_draft_generator/src"]