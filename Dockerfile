FROM python:3.7-slim-stretch

RUN apt-get update \
&& apt-get -y install tesseract-ocr tesseract-ocr-eng python-opencv

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY infinitewisdom/ infinitewisdom/
COPY infinitewisdom/bot.py bot.py


CMD [ "python", "./bot.py" ]
