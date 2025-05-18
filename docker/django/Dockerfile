# Base image
FROM python:3.12-slim

ARG ENV=debug

# Installing dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy requirements.txt from the root of the project
COPY requirements/production.txt ./requirements.txt

RUN pip install -r requirements.txt

# Installing debugger for debug
RUN if [ "$ENV" = "debug" ]; then pip install django-debug-toolbar; fi

# Copy all the project files
COPY . ./

COPY ./backend/apps/reports/fonts /usr/share/fonts/truetype/dejavu/

# Specify the correct PYTHONPATH and settings
ENV PYTHONPATH=/app/backend
ENV DJANGO_SETTINGS_MODULE=backend.config.settings.base

# For production: static assembly
RUN if [ "$ENV" = "release" ]; then \
    python manage.py collectstatic --noinput; \
  fi

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]