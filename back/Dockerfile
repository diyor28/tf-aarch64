FROM python:3.9.4 as python-build
RUN apt-get update && apt-get install -y docker.io
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD python migrate.py && gunicorn --bind=0.0.0.0 --access-logfile '-' main:app -k uvicorn.workers.UvicornWorker
