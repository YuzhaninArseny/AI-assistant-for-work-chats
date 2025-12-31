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

RUN mkdir -p /app/models

EXPOSE 8084

RUN python -c "import sys; from transformers import AutoTokenizer, AutoModelForCausalLM; import torch; print('=== НАЧАЛО ЗАГРУЗКИ МОДЕЛИ ===', file=sys.stderr); print('1. Загрузка токенизатора...', file=sys.stderr); sys.stderr.flush(); AutoTokenizer.from_pretrained('Qwen/Qwen2.5-1.5B-Instruct', use_fast=True, trust_remote_code=True); print('Токенизатор загружен', file=sys.stderr); print('2. Загрузка модели (это займет 2-5 минут)...', file=sys.stderr); sys.stderr.flush(); AutoModelForCausalLM.from_pretrained('Qwen/Qwen2.5-1.5B-Instruct', torch_dtype=torch.float32, trust_remote_code=True, low_cpu_mem_usage=True, device_map='cpu'); print('Модель загружена успешно!', file=sys.stderr); print('=== ЗАГРУЗКА ЗАВЕРШЕНА ===', file=sys.stderr);"

CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8084"]



