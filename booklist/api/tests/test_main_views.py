# -*- coding: utf-8 -*-

from books.models import Author, Book
from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class TestUserViewSet(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser", email="test@example.com", password="testpass123"
        )
        self.list_url = reverse("user-list")
        self.detail_url = reverse("user-detail", kwargs={"pk": self.user.pk})

    def test_user_list(self):
        """Test GET /api/users/ returns user list"""
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1  # type: ignore
        assert response.data[0]["username"] == self.user.username  # type: ignore

    def test_user_detail(self):
        """Test GET /api/users/{id}/ returns user details"""
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == self.user.username  # type: ignore
        assert response.data["email"] == self.user.email  # type: ignore

    def test_user_create(self):
        """Test POST /api/users/ creates new user"""
        data = {
            "username": "newuser",
            "email": "new@example.com",
            "password": "newpass123",
        }
        response = self.client.post(self.list_url, data=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert User.objects.filter(username="newuser").exists()

    def test_user_update(self):
        """Test PUT /api/users/{id}/ updates user"""
        data = {
            "username": "updateduser",
            "email": "updated@example.com",
        }
        response = self.client.put(self.detail_url, data=data)
        assert response.status_code == status.HTTP_200_OK
        self.user.refresh_from_db()
        assert self.user.username == "updateduser"

    def test_user_delete(self):
        """Test DELETE /api/users/{id}/ deletes user"""
        response = self.client.delete(self.detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not User.objects.filter(pk=self.user.pk).exists()


class TestBookViewSet(APITestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Test Author")

        self.book1 = Book.objects.create(
            title="Book 1",
            isbn="1111111111111",
        )
        self.book1.authors.add(self.author)

        self.book2 = Book.objects.create(
            title="Book 2",
            isbn="2222222222222",
        )
        self.book2.authors.add(self.author)

        self.list_url = reverse("book-list")
        self.detail_url = reverse("book-detail", kwargs={"pk": self.book1.pk})

    def test_book_list(self):
        """Test GET /api/books/ returns book list"""
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK

        books = response.data  # type: ignore
        assert len(books) == 2

    def test_book_detail(self):
        """Test GET /api/books/{id}/ returns book details"""
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == self.book1.title  # type: ignore
        assert response.data["isbn"] == self.book1.isbn  # type: ignore

    def test_book_create(self):
        """Test POST /api/books/ creates book"""
        data = {
            "title": "New Book",
            "isbn": "3333333333333",
            "authors": [self.author.pk],
            "description": "A new book",
        }
        response = self.client.post(self.list_url, data=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Book.objects.filter(isbn="3333333333333").exists()

    def test_book_update(self):
        """Test PUT /api/books/{id}/ updates book"""
        data = {
            "title": "Updated Book",
            "isbn": self.book1.isbn,
            "authors": [self.author.pk],
            "description": "Updated description",
        }
        response = self.client.put(self.detail_url, data=data)
        assert response.status_code == status.HTTP_200_OK

        self.book1.refresh_from_db()
        assert self.book1.title == "Updated Book"

    def test_book_delete(self):
        """Test DELETE /api/books/{id}/ deletes book"""
        response = self.client.delete(self.detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Book.objects.filter(pk=self.book1.pk).exists()


class TestAuthorViewSet(APITestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Test Author")
        self.list_url = reverse("author-list")
        self.detail_url = reverse("author-detail", kwargs={"pk": self.author.pk})

    def test_author_list(self):
        """Test GET /api/authors/ returns author list"""
        response = self.client.get(self.list_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1  # type: ignore

    def test_author_detail(self):
        """Test GET /api/authors/{id}/ returns author details"""
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == self.author.name  # type: ignore

    def test_author_create(self):
        """Test POST /api/authors/ creates new author"""
        data = {"name": "New Author"}
        response = self.client.post(self.list_url, data=data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Author.objects.filter(name="New Author").exists()

    def test_author_update(self):
        """Test PUT /api/authors/{id}/ updates author"""
        data = {"name": "Updated Author"}
        response = self.client.put(self.detail_url, data=data)
        assert response.status_code == status.HTTP_200_OK
        self.author.refresh_from_db()
        assert self.author.name == "Updated Author"

    def test_author_delete(self):
        """Test DELETE /api/authors/{id}/ deletes author"""
        response = self.client.delete(self.detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not Author.objects.filter(pk=self.author.pk).exists()
