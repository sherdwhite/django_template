# encoding: utf-8

import logging
import random

from books.models import Author
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

logger = logging.getLogger(__name__)


class TestAuthorEndpoints(APITestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Såm Lake")

        self.full_data = {"name": self.author.name}

        self.detail_url = reverse("author-detail", kwargs={"pk": self.author.pk})
        self.list_url = reverse("author-list")

    def test_get_author(self):
        r"""GET /api/author/\d+/ should return the author"""
        response = self.client.get(self.detail_url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data["pk"] == self.author.pk  # type: ignore
        assert response.data["name"] == self.author.name  # type: ignore

    def test_patch_author(self):
        r"""PATCH /api/author/\d+/ should update the author"""
        expected_name = "Story-bot"
        response = self.client.patch(self.detail_url, data={"name": expected_name})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["name"] == expected_name  # type: ignore

    def test_put_author(self):
        """PUT /api/author/{author.pk}/ should update the author"""
        expected_name = "Story-bot"
        self.full_data["name"] = expected_name
        response = self.client.put(self.detail_url, data=self.full_data)
        assert response.data["name"] == expected_name  # type: ignore
        updated_author = Author.objects.first()
        assert updated_author is not None
        assert updated_author.name == expected_name

    def test_delete_author(self):
        """DELETE /api/author/{author.pk}/ should delete the author"""
        expected_authors = Author.objects.count() - 1
        response = self.client.delete(self.detail_url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Author.objects.count() == expected_authors

    def test_post_author(self):
        """POST /api/author/ should create a author"""
        expected_authors = Author.objects.count() + 1
        response = self.client.post(self.list_url, data=self.full_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Author.objects.count() == expected_authors

    def test_list_author(self):
        """GET /api/author/ should list all authors"""
        num_created = random.randint(5, 10)
        expected_authors = Author.objects.count() + num_created
        for i in range(num_created):
            Author.objects.create(name=f"Story-bot {i}")

        response = self.client.get(self.list_url)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == expected_authors  # type: ignore
        # type: ignore on next line for pylance response.data issue
        response_data = response.data  # type: ignore
        for author, response_item in zip(Author.objects.all(), response_data):
            assert response_item["pk"] == author.pk
