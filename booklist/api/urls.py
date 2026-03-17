from django.urls import include, path

# API versioning - this allows for /api/v1/ and future versions
urlpatterns = [
    # Versioned API endpoints
    path("v1/", include("api.v1.urls")),
    # Future API versions can be added here:
    # path('v2/', include('api.v2.urls')),  # When v2 is ready
    # Authentication URLs for browsable API
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # Default to v1 for backward compatibility (optional)
    # This allows existing clients using /api/books/ to continue working
    path("", include("api.v1.urls")),
]
