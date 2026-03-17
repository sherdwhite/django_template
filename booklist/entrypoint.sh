#!/bin/sh

# Run database migrations
python manage.py migrate

# Start the application server
exec uvicorn core.asgi:application --host 0.0.0.0 --port 8000
