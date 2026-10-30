# Static Files and Media Guide

This document explains how static assets and user-uploaded media files are handled in the BookList project.

## Current Setup

- **Frontend Styling**: Bootstrap 5.3.3 via CDN with custom overrides in `booklist/static/css/custom.css`.
- **Static File Serving**: Served directly by **Nginx** via shared Docker volume in production / docker-compose, bypassing Django worker processes.
- **Media File Serving**: Uploaded media (book covers, user avatars) stored in a shared persistent volume and served by Nginx (in production) or Django `urlpatterns` (when `DEBUG=True` in local development).

---

## Django Configuration

Static and media files are configured in `booklist/core/settings.py`:

```python
# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = Path(os.environ.get("STATIC_ROOT", BASE_DIR / "staticfiles"))

# Media files (user uploads: avatars, book covers, etc.)
MEDIA_URL = os.environ.get("MEDIA_URL", "/media/")
MEDIA_ROOT = Path(os.environ.get("MEDIA_ROOT", BASE_DIR / "media"))
```

In `booklist/core/urls.py`, local development media serving is enabled during `DEBUG`:

```python
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Directory Structure

```
booklist/
├── static/                 # Source static files (development)
│   ├── css/               # Custom CSS files
│   │   └── custom.css     # Project-specific styles
│   ├── js/                # Custom JavaScript files
│   └── images/            # Project images
├── staticfiles/           # Local collected static files (when running without Docker)
│   ├── admin/             # Django admin static files
│   ├── rest_framework/    # DRF static files
│   └── css/               # Collected custom CSS
└── media/                 # Local uploaded files (when running without Docker)
```

---

## Docker & Production Architecture

In containerized environments (both Docker Compose and DevContainer):

1. **Volume Mounts**:
   - `static`: Shared volume mounted at `/static` in both Django and Nginx.
   - `media_data`: Shared persistent volume mounted at `/media` in both Django and Nginx.

2. **Build Time**:
   - During `docker build`, the `Dockerfile` pre-creates `/static` and `/media` with non-root `appuser` ownership.
   - Runs `python manage.py collectstatic --noinput` to populate `/static`.

3. **Nginx Reverse Proxy**:
   Nginx serves both locations directly for maximum throughput and minimal backend load:
   ```nginx
   # Static assets (1 year immutable cache)
   location /static/ {
       alias /static/;
       expires 1y;
       add_header Cache-Control "public, immutable";
       access_log off;
       log_not_found off;
   }

   # User uploads (1 year cache)
   location /media/ {
       alias /media/;
       expires 1y;
       add_header Cache-Control "public";
       access_log off;
       log_not_found off;
   }
   ```

---

## Bootstrap Integration

### CDN Implementation (Default)

Bootstrap is loaded from CDN in `templates/base.html`:

```html
<!-- Bootstrap CSS -->
<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css"
      rel="stylesheet"
      integrity="sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH"
      crossorigin="anonymous">

<!-- Custom CSS (loaded after Bootstrap) -->
<link rel="stylesheet" href="{% static 'css/custom.css' %}">

<!-- Bootstrap JS -->
<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"
        integrity="sha384-YvpcrYf0tY3lHB60NNkmXc5s9fDVZLESaAA55NDzOxhy9GkcIdslK1eN7N6jIeHz"
        crossorigin="anonymous"></script>
```

---

## Custom Styles

Project-specific styles are defined in `booklist/static/css/custom.css`. This file:
- Loads after Bootstrap CSS (allowing overrides).
- Contains custom component styles.
- Follows Bootstrap's CSS custom property patterns.

Example custom styles:
```css
/* Override Bootstrap variables */
:root {
  --bs-primary: #007bff;
}

/* Custom component styles */
.book-card {
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s ease-in-out;
}
```

---

## Manual Collection & Commands

To manually collect static files:

```bash
# Using Makefile
make collectstatic

# Using Docker Compose directly
docker compose exec booklist python manage.py collectstatic --noinput

# In local Python environment
python manage.py collectstatic --noinput
```
