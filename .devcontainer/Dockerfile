# Dev Container Dockerfile
# This is specifically for VS Code DevContainer development on Linux
# Benefits: Matches host UID/GID for proper file permissions, SELinux compatible

FROM python:3.14-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/workspace/booklist/
ENV DJANGO_SETTINGS_MODULE=core.settings
ENV DEBUG=True
ENV DJANGO_DEBUG=True
ENV DJANGO_ENV=development
ENV STATIC_ROOT=/static
ENV MEDIA_ROOT=/media

# Create a non-root user that matches common Linux host UIDs
# This prevents permission issues on Linux systems (especially Fedora/RHEL)
ARG USER_UID=1000
ARG USER_GID=1000
RUN groupadd -g ${USER_GID} appuser && \
    useradd -m -u ${USER_UID} -g ${USER_GID} -s /bin/bash appuser

# Install system dependencies in one layer
RUN apt-get update && apt-get install -y \
    postgresql-client \
    git \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies as root (before switching to non-root user)
COPY booklist/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Pre-create VS Code server directories with correct ownership
# This prevents permission errors when VS Code tries to create these as appuser
RUN mkdir -p /home/appuser/.vscode-server/bin \
             /home/appuser/.vscode-server/data/Machine \
             /home/appuser/.vscode-server/extensions \
    && chown -R appuser:appuser /home/appuser/.vscode-server

# Pre-create the static and media volume mount points with correct ownership
# This allows collectstatic and file uploads to write to the shared Docker volume
RUN mkdir -p /static /media && chown -R appuser:appuser /static /media

# Set working directory
WORKDIR /workspace/booklist

# Switch to non-root user
USER appuser
