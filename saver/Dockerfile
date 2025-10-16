FROM python:3.12-slim

ENV POETRY_VERSION=2.2.1
WORKDIR /app

RUN pip install "poetry==${POETRY_VERSION}" && poetry --version

COPY pyproject.toml poetry.lock* ./

RUN poetry config virtualenvs.create false

RUN --mount=type=cache,target=/root/.cache/pip \
    --mount=type=cache,target=/root/.cache/pypoetry \
    poetry install --no-interaction --no-ansi --no-root

COPY src/ ./src/
ENV PYTHONPATH=/app/src
# RUN poetry install --only-root --no-interaction --no-ansi
CMD ["ls", "src/saver_app"]
CMD ["uvicorn", "src.saver_app.main:app", "--host", "0.0.0.0", "--port", "8000"]
