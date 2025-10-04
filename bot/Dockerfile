FROM python:3.12-alpine

WORKDIR /bot

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY bot.py .
COPY tgbot tgbot

ENTRYPOINT ["python", "bot.py"]