FROM python:3.7-slim-stretch

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY bot.py bot.py

CMD [ "python", "./bot.py" ]
