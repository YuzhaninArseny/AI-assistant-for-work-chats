FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VERSION=2.2.1

WORKDIR /app

RUN pip install "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root

COPY . /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

EXPOSE 8082

CMD ["uvicorn", "api:app", \
     "--host", "0.0.0.0", "--port", "8082", \
     "--reload", "--reload-dir", "/app/src"]