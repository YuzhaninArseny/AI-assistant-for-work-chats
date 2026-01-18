FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_VERSION=2.2.1 \
    HF_HUB_DISABLE_PROGRESS_BARS=1 \
    HF_HUB_DOWNLOAD_TIMEOUT=1800 \
    HF_HUB_REQUEST_TIMEOUT=1800 \
    HF_TRANSFER_MAX_RETRIES=5 \
    TRANSFORMERS_CACHE=/app/models \
    HF_HOME=/app/models

WORKDIR /app

RUN pip install "poetry==${POETRY_VERSION}"

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-root

COPY . /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/src"

# Создаем директорию для моделей
RUN mkdir -p /app/models

EXPOSE 8083

# Загружаем модель при сборке
RUN python -c "import sys; from transformers import GPT2Tokenizer, T5ForConditionalGeneration; print('=== НАЧАЛО ЗАГРУЗКИ МОДЕЛИ ===', file=sys.stderr); print('1. Загрузка токенизатора...', file=sys.stderr); sys.stderr.flush(); tokenizer = GPT2Tokenizer.from_pretrained('RussianNLP/FRED-T5-Summarizer'); print('Токенизатор загружен', file=sys.stderr); print('2. Загрузка модели (это займет 2-5 минут)...', file=sys.stderr); sys.stderr.flush(); model = T5ForConditionalGeneration.from_pretrained('RussianNLP/FRED-T5-Summarizer'); print('Модель загружена успешно!', file=sys.stderr); print('=== ЗАГРУЗКА ЗАВЕРШЕНА ===', file=sys.stderr);"

# Запускаем приложение
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8083"]