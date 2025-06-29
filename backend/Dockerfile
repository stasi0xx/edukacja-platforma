# backend/Dockerfile
FROM python:3.11

WORKDIR /app

RUN apt-get update && apt-get install -y git

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ .

# Ustaw zmienne środowiskowe Django
ENV DJANGO_SETTINGS_MODULE=config.settings
ENV PYTHONUNBUFFERED=1

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]