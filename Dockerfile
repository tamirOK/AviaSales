FROM python:3.7-slim

COPY via3.xml via3.xml
COPY viaow.xml viaow.xml
COPY requirements.txt ./requirements.txt

RUN pip install -r requirements.txt

COPY app /app

ENV PYTHONUNBUFFERED 1
ENV FLASK_APP=app/__init__.py
ENV FLASK_ENV=development
RUN flask populate-db

CMD flask run
