FROM python:3.9.4 as python-build
RUN apt-get update; apt-get install docker.io -y
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD gunicorn main:app -k uvicorn.workers.UvicornWorker
