FROM python:3.7-slim-stretch

RUN apt-get update \
&& apt-get -y install tesseract-ocr tesseract-ocr-eng

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY infinitewisdom/ infinitewisdom/

WORKDIR /app/infinitewisdom

CMD [ "python", "./bot.py" ]
