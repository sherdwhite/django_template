# Use the official Python image as the base image
FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/booklist/
ENV DJANGO_SETTINGS_MODULE=core.settings

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

# Collect static files during build
RUN python manage.py collectstatic --noinput

# Create non-root user for runtime security
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Make entrypoint executable
RUN chmod +x entrypoint.sh

# Switch to non-root user
USER appuser

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
