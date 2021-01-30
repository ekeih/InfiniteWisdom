FROM python:3.8-slim-buster

ENV PYTHONUNBUFFERED=1

RUN apt-get update \
&& apt-get -y install tesseract-ocr tesseract-ocr-eng libsm6 python-opencv \
libpq-dev

WORKDIR /app

COPY poetry.lock pyproject.toml ./
RUN pip install "poetry==$POETRY_VERSION" \
 && POETRY_VIRTUALENVS_CREATE=false poetry install \
 && pip uninstall -y poetry \
 && pip install --no-cache-dir psycopg2

COPY . .

CMD [ "python", "./infinitewisdom/main.py" ]
