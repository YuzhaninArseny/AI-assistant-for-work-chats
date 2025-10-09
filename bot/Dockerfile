FROM python:3.12-alpine

WORKDIR /bot

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY src/bot_app/bot_main.py .
COPY src/bot_app/api/api.py .
COPY src/bot_app tgbot

ENTRYPOINT ["python", "bot.py"]