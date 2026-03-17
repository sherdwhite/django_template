from api.serializers import (
    AuthorSerializer,
    BookSerializer,
    UserSerializer,
)
from books.models import Author, Book
from django.contrib.auth.models import User
from rest_framework import viewsets


class UserViewSet(viewsets.ModelViewSet):
    """API endpoint that allows users to be viewed or edited."""

    queryset = User.objects.all()
    serializer_class = UserSerializer


class BookViewSet(viewsets.ModelViewSet):
    """API endpoint that allows books to be viewed or edited."""

    queryset = Book.objects.all()
    serializer_class = BookSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    """API endpoint that allows authors to be viewed or edited."""

    queryset = Author.objects.all()
    serializer_class = AuthorSerializer
