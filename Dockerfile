FROM python:3.7-slim-stretch

RUN apt-get update \
&& apt-get -y install tesseract-ocr tesseract-ocr-eng libsm6 python-opencv

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

CMD [ "python", "./infinitewisdom/main.py" ]
