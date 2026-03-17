from django.urls import include, path
from rest_framework import routers

from . import views

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet)
router.register(r"books", views.BookViewSet)
router.register(r"authors", views.AuthorViewSet)

urlpatterns = [
    path("", include(router.urls)),
]
