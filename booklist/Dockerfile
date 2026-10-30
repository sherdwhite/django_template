# Use the official Python image as the base image
FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/booklist/
ENV DJANGO_SETTINGS_MODULE=core.settings
ENV STATIC_ROOT=/static
ENV MEDIA_ROOT=/media

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Set working directory
WORKDIR /booklist

# Copy and install Python dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Pre-create static and media directories and non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser && \
    mkdir -p /static /media && chown -R appuser:appuser /static /media

# Collect static files during build to /static
RUN python manage.py collectstatic --noinput && chown -R appuser:appuser /static

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Switch to non-root user
USER appuser

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
