# Static Files and CSS Framework Guide

This document explains how static files are handled in the Book List project.

## Current Setup

The project uses **Bootstrap 5.3.3 via CDN** for CSS framework functionality.

## Static Files Configuration

Django static files are configured in `booklist/settings.py`:

```python
STATIC_URL = "static/"
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
STATIC_ROOT = BASE_DIR / "staticfiles"
```

### Directory Structure

```
booklist/
├── static/                 # Source static files (development)
│   ├── css/               # Custom CSS files
│   │   └── custom.css     # Project-specific styles
│   ├── js/                # Custom JavaScript files
│   └── images/            # Project images
└── staticfiles/           # Collected static files (production)
    ├── admin/             # Django admin static files
    ├── rest_framework/    # DRF static files
    └── css/               # Collected custom CSS
        └── custom.css
```

## Bootstrap Integration

### CDN Implementation (Current)

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

## Custom Styles

Project-specific styles are defined in `booklist/static/css/custom.css`. This file:
- Loads after Bootstrap CSS (allowing overrides)
- Contains custom component styles
- Includes responsive adjustments
- Follows Bootstrap's CSS custom property patterns

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

## Production Considerations

### Static File Collection

For production deployment, collect static files:
```bash
python manage.py collectstatic --noinput
```

This copies custom CSS and other static files from `STATICFILES_DIRS` to `STATIC_ROOT` for serving by the web server.

### Content Security Policy (CSP)

When using CDN resources, consider implementing CSP headers that allow Bootstrap CDN:
```
Content-Security-Policy: style-src 'self' https://cdn.jsdelivr.net; script-src 'self' https://cdn.jsdelivr.net
```

## Alternative: Local Bootstrap Files

If you need to use local Bootstrap files (for offline development or security requirements):

1. **Download Bootstrap:**
   ```bash
   # Download and extract to booklist/static/vendor/bootstrap/
   mkdir -p booklist/static/vendor/bootstrap
   # Place bootstrap.min.css and bootstrap.bundle.min.js in respective css/ and js/ folders
   ```

2. **Update templates/base.html:**
   ```html
   <!-- Replace CDN links with: -->
   <link rel="stylesheet" href="{% static 'vendor/bootstrap/css/bootstrap.min.css' %}">
   <script src="{% static 'vendor/bootstrap/js/bootstrap.bundle.min.js' %}"></script>
   ```

3. **Run collectstatic for production:**
   ```bash
   python manage.py collectstatic
   ```

**Note:** CDN approach avoids local file management.
