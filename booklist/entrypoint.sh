#!/bin/sh
set -e

# If arguments are passed (e.g., manage.py commands, pytest, shell), execute them directly
if [ $# -gt 0 ]; then
    exec "$@"
fi

# Production ASGI server using Gunicorn process manager with Uvicorn worker class
# Concurrency configuration: defaults to WEB_CONCURRENCY or 4 worker processes
WORKERS=${WEB_CONCURRENCY:-4}
TIMEOUT=${WEB_TIMEOUT:-60}
GRACEFUL_TIMEOUT=${WEB_GRACEFUL_TIMEOUT:-30}

echo "Starting Gunicorn with ${WORKERS} Uvicorn ASGI workers..."
exec gunicorn core.asgi:application \
    -k uvicorn.workers.UvicornWorker \
    --bind 0.0.0.0:8000 \
    --workers "${WORKERS}" \
    --timeout "${TIMEOUT}" \
    --graceful-timeout "${GRACEFUL_TIMEOUT}" \
    --worker-tmp-dir /dev/shm \
    --access-logfile - \
    --error-logfile -
