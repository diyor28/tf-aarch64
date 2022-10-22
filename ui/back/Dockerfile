FROM python:3.9.4 as python-build
WORKDIR /app
ENV PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
RUN apt-get update; apt-get install docker.io -y
CMD uvicorn main:app --host 0.0.0.0 --port 8000
