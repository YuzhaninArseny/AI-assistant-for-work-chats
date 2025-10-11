FROM python:3.12-alpine

WORKDIR /app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt


COPY src/ ./src/
ENV PYTHONPATH=src/
CMD ["ls"]
CMD ["python", "-m", "src.bot_app.bot_main"]