FROM python:3.12

RUN mkdir /weather-api

WORKDIR /weather-api

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "app.main:app", "--workers", "4", "--worker-class", "uvicorn.workers.Uvicornworker", "--bind=0.0.0.0:8000"]
