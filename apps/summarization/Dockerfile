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
ENV TRANSFORMERS_CACHE="/app/models"
ENV HF_HOME="/app/models"

# Создаем директорию для моделей
RUN mkdir -p /app/models

EXPOSE 8083

# Загружаем модель при запуске через скрипт
CMD ["sh", "-c", "python -c \"\
from transformers import GPT2Tokenizer, T5ForConditionalGeneration; \
import os; \
print('📥 Загружаю модель...'); \
tokenizer = GPT2Tokenizer.from_pretrained('RussianNLP/FRED-T5-Summarizer'); \
model = T5ForConditionalGeneration.from_pretrained('RussianNLP/FRED-T5-Summarizer'); \
print('✅ Модель загружена!'); \
\" && uvicorn api:app --host 0.0.0.0 --port 8083 --reload --reload-dir /app/src"]