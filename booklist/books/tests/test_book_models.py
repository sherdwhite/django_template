# encoding: utf-8
from books.models import Author, Book
from django.test import TestCase


class TestBooks(TestCase):
    def setUp(self):
        self.author = Author.objects.create(name="Óoly Y")
        self.book = Book.objects.create(
            title="The Road of the Rune",
            isbn="1234567890123",
        )
        self.book.authors.add(self.author)

    def test_book_str(self):
        """Book __str__ should return the title"""
        assert str(self.book) == "The Road of the Rune"

    def test_author_names(self):
        """book.author_names should return comma-separated author names"""
        assert self.book.author_names == "Óoly Y"

    def test_author_str(self):
        """Author __str__ should return the name"""
        assert str(self.author) == "Óoly Y"
