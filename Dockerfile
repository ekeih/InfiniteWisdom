FROM python:3.7-slim-stretch

RUN apt-get update \
&& apt-get -y install tesseract-ocr tesseract-ocr-eng

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY stats.py stats.py
COPY analysis.py analysis.py
COPY persistence.py persistence.py
COPY config.py config.py
COPY const.py const.py
COPY bot.py bot.py

CMD [ "python", "./bot.py" ]
