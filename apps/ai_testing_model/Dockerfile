# syntax=docker/dockerfile:1.7-labs
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONPATH="/app/saver/src:/app/shared/src"

WORKDIR /app

RUN pip install fastapi uvicorn

COPY main.py /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8888"]