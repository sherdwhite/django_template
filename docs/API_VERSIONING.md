# API Versioning Implementation

This document explains the API versioning structure implemented for the BookList API.

## Structure

```
api/
├── __init__.py
├── apps.py
├── urls.py              # Main API routing with versioning
├── v1/                  # Version 1 API
│   ├── __init__.py
│   ├── urls.py         # V1 specific routes
│   ├── views.py        # V1 viewsets
│   └── serializers.py  # V1 serializers
└── tests/              # API tests

# Future structure (when implementing v2):
# ├── v2/                  # Version 2 API
# │   ├── __init__.py
# │   ├── urls.py         # V2 specific routes
# │   └── views.py        # V2 viewsets (with enhanced features)
```

## URL Patterns

1. **Versioned endpoints:**
   - `/api/v1/books/` - Version 1 books endpoint
   - `/api/v1/authors/` - Version 1 authors endpoint
   - `/api/v1/users/` - Version 1 users endpoint

2. **Backward compatibility:**
   - `/api/books/` - Still works (routes to v1)
   - `/api/authors/` - Still works (routes to v1)
   - etc.

3. **Future versions (when implemented):**
   - `/api/v2/books/` - Ready when you implement v2

---

## Gateway & Reverse Proxy Handling

All API traffic passing through Nginx includes:
- **Rate Limiting**: Protected by an `api_limit` zone in Nginx (30 requests/second with burst 20, returning HTTP `429 Too Many Requests`).
- **Connection Reuse**: Uses HTTP/1.1 with backend keepalive pools to reduce TCP handshakes.
- **Client IP Tracking**: Standard `X-Real-IP` and `X-Forwarded-For` proxy headers forwarded for rate limiting and DRF auditing.

---

## Adding a New Version

To add a new API version (e.g., v2):

1. Create a new directory: `api/v2/`
2. Copy the structure from `v1/` as a starting point
3. Modify the views/serializers for new features
4. Add the URL pattern in `api/urls.py`:
   ```python
   path('v2/', include('api.v2.urls')),
   ```

## Migration Strategy

When you're ready to add new features:

1. Keep v1 unchanged for existing clients
2. Implement new features in v2
3. Document the differences between versions
4. Provide migration guides for clients
5. Eventually deprecate older versions with proper notice
