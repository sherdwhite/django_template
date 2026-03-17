# encoding: utf-8

import logging
import random

from books.models import Author, Book
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

logger = logging.getLogger(__name__)


class TestBookEndpoints(APITestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Såm Lake")
        self.book = Book.objects.create(
            title="Heraldic Wîng",
            isbn="1234567890123",
        )
        self.book.authors.add(self.author)

        self.full_data = {
            "title": self.book.title,
            "isbn": self.book.isbn,
            "description": "High fantasy",
            "authors": [self.author.pk],
        }

        self.detail_url = reverse("book-detail", kwargs={"pk": self.book.pk})
        self.list_url = reverse("book-list")

    def test_get_book(self):
        """GET /api/book/{book.pk}/ should return the book"""
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["pk"] == self.book.pk  # type: ignore
        assert response.data["title"] == self.book.title  # type: ignore
        expected_authors = [a.pk for a in self.book.authors.all()]
        assert response.data["authors"] == expected_authors  # type: ignore

    def test_patch_book(self):
        """PATCH /api/book/{book.pk}/ should update the book"""
        expected_description = (
            "In a hole there lived a creepy, grey alien named Sonya Grey. "
            "Not a backward, hot, tall hole, filled with stamps and a greasy smell, "
            "nor yet a violent, charming, pretty hole with nothing in it to sit "
            "down on or to eat: it was an alien-hole, and that means shelter."
        ).strip()
        response = self.client.patch(
            self.detail_url, data={"description": expected_description}
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["description"] == expected_description  # type: ignore

    def test_put_book(self):
        """PUT /api/book/{book.pk}/ should update the book"""
        expected_description = "Totally informative description"
        self.full_data["description"] = expected_description
        response = self.client.put(self.detail_url, data=self.full_data)
        assert response.data["description"] == expected_description  # type: ignore
        updated_book = Book.objects.first()
        assert updated_book is not None
        assert updated_book.description == expected_description

    def test_delete_book(self):
        """DELETE /api/book/{book.pk}/ should delete the book"""
        expected_books = Book.objects.count() - 1
        response = self.client.delete(self.detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Book.objects.count() == expected_books

    def test_post_book(self):
        """POST /api/book/ should create a book"""
        expected_books = Book.objects.count() + 1
        # Use a different ISBN to avoid unique constraint violation
        test_data = self.full_data.copy()
        test_data["isbn"] = "9876543210987"
        response = self.client.post(self.list_url, data=test_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Book.objects.count() == expected_books

    def test_list_book(self):
        """GET /api/book/ should list all books"""
        num_created = random.randint(5, 10)
        expected_books = Book.objects.count() + num_created
        for i in range(num_created):
            Book.objects.create(
                title=f"The Neverending Series {i}",
                isbn=f"111111111111{i}",
            )

        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == expected_books  # type: ignore
        # type: ignore on next line for pylance response.data issue
        response_data = response.data  # type: ignore
        for book, response_item in zip(Book.objects.all(), response_data):
            assert response_item["pk"] == book.pk
