# Database Connection Pooling Configuration

This document explains the database connection pooling and PostgreSQL performance settings in the BookList application.

## What is Connection Pooling?

Connection pooling manages database connections by:
- Reusing existing connections instead of establishing new TCP/TLS connections on every request
- Maintaining a pool of persistent connections across HTTP requests
- Closing idle connections after a timeout period
- Verifying connection health before query execution (`CONN_HEALTH_CHECKS`)

## Configuration

### Environment Variables

The following environment variables control database connections and pooling:

- `DJANGO_ENV`: Set to `production` for production-level pooling settings and strict PostgreSQL validation.
- `DB_CONN_MAX_AGE`: Connection lifetime in seconds.
  - Development default: `300` seconds (5 minutes).
  - Production default: `600` seconds (10 minutes).
  - Production Docker Compose (`docker-compose.prod.yml`): `3600` seconds (1 hour).
- `DB_CONNECT_TIMEOUT`: Connection timeout in seconds (`10` in dev, `30` in prod).
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: Standard database connection credentials.

### Django Settings Implementation

In `booklist/core/settings.py`:

```python
if os.environ.get("DB_HOST"):
    conn_max_age = int(
        os.environ.get("DB_CONN_MAX_AGE", "600" if IS_PRODUCTION else "300")
    )
    connect_timeout = int(
        os.environ.get("DB_CONNECT_TIMEOUT", "30" if IS_PRODUCTION else "10")
    )
    DATABASES = {
        "default": {
            "ENGINE": os.environ.get(
                "DB_ENGINE", "django.db.backends.postgresql"
            ),
            "NAME": os.environ.get("DB_NAME", "postgres"),
            "USER": os.environ.get("DB_USER", "postgres"),
            "PASSWORD": os.environ.get(
                "DB_PASSWORD",
                os.environ.get("POSTGRES_PASSWORD", "postgres"),
            ),
            "HOST": os.environ.get("DB_HOST", "db"),
            "PORT": os.environ.get("DB_PORT", "5432"),
            "OPTIONS": {
                "connect_timeout": connect_timeout,
            },
            # Connection pooling / persistent connections
            "CONN_MAX_AGE": conn_max_age,
            "CONN_HEALTH_CHECKS": True,
        }
    }
elif IS_PRODUCTION:
    raise RuntimeError(
        "Production environment requires DB_HOST to be set for PostgreSQL. "
        "Silent fallback to SQLite is disabled in production."
    )
```

- **`CONN_MAX_AGE`**: Enables persistent connections for the specified duration instead of closing the connection at the end of each request.
- **`CONN_HEALTH_CHECKS: True`**: Verifies that existing connections are still alive before executing queries, preventing stale connection errors after timeouts or network blips.

---

## Production PostgreSQL Tuning

In `docker-compose.prod.yml`, the PostgreSQL 17 database service is tuned for high concurrency workloads:

- **Authentication**: Modern `scram-sha-256` password hashing instead of legacy `md5`.
- **Memory & Buffers**:
  - `shared_buffers=512MB`: Dedicated memory cache for database pages.
  - `effective_cache_size=1536MB`: Informs planner about available filesystem cache.
  - `work_mem=16MB`: Memory for complex sorting and hash operations per query.
  - `maintenance_work_mem=128MB`: Memory for maintenance tasks (vacuuming, indexing).
- **WAL & Checkpoints**:
  - `min_wal_size=1GB`, `max_wal_size=4GB`.
  - `checkpoint_completion_target=0.9`: Smooths disk I/O over time.
  - `wal_buffers=16MB`.
- **Concurrency & Concurrency Limits**:
  - `max_connections=200`: Maximum simultaneous database connections.
  - `effective_io_concurrency=200`: Concurrent asynchronous I/O requests for SSD/NVMe.

---

## Usage

### Development

```bash
docker-compose up -d
```

### Production Migrations & Deployment

In production, run database migrations as an isolated pre-deployment step rather than running them automatically during container startup:

```bash
# 1. Run migrations
make prod-migrate

# Or using docker compose directly:
docker-compose -f docker-compose.yml -f docker-compose.prod.yml run --rm booklist python manage.py migrate

# 2. Start production services
make prod-up
```

---

## Monitoring

Monitor your connection pool and database health:

```bash
# Check database connectivity and Django health check
python manage.py check --database default

# Monitor service health (includes database healthcheck)
make health

# Check Docker service status
docker compose ps

# View database logs
docker compose logs -f db

# Monitor active connections (requires database access)
python manage.py dbshell
# Inside psql, run:
# SELECT count(*) FROM pg_stat_activity;
```

### Health Checks

The application includes automated health checks:
- **Database**: `pg_isready -U postgres` (every 10s in dev, 30s in prod)
- **Django**: `python manage.py check --database default` (every 30s)
- **Redis**: `redis-cli ping` (every 10s in dev, 30s in prod)
- **Recovery**: Docker restarts unhealthy containers automatically (`restart: unless-stopped`).
