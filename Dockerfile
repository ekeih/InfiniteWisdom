FROM python:3.8-slim-buster

RUN apt-get update \
&& apt-get -y install tesseract-ocr tesseract-ocr-eng libsm6 python-opencv \
libpq-dev

WORKDIR /app

RUN pip install --no-cache-dir psycopg2
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD [ "python", "./infinitewisdom/main.py" ]
