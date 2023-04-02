# syntax=docker/dockerfile:1.4
FROM python:3.10-alpine AS builder
EXPOSE 8000
WORKDIR /app
RUN apk update 
RUN apk add python3-dev gcc libc-dev
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY . /app 
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]