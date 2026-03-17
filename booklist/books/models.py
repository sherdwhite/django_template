# encoding: utf-8

from django.db import models


class Book(models.Model):
    title = models.CharField(max_length=255)
    authors = models.ManyToManyField("Author", related_name="books")
    description = models.TextField(blank=True)
    isbn = models.CharField(max_length=255, unique=True, help_text="ISBN-10 or ISBN-13")

    # Book Details
    publication_date = models.DateField(blank=True, null=True)
    page_count = models.PositiveIntegerField(blank=True, null=True)
    language = models.CharField(
        max_length=10, default="en", help_text="Language code (e.g., en, es, fr)"
    )

    # Categories
    GENRE_CHOICES = [
        ("fiction", "Fiction"),
        ("non_fiction", "Non-Fiction"),
        ("mystery", "Mystery"),
        ("romance", "Romance"),
        ("sci_fi", "Science Fiction"),
        ("fantasy", "Fantasy"),
        ("biography", "Biography"),
        ("history", "History"),
        ("self_help", "Self Help"),
        ("business", "Business"),
        ("textbook", "Textbook"),
        ("children", "Children"),
        ("young_adult", "Young Adult"),
        ("other", "Other"),
    ]
    genre = models.CharField(max_length=20, choices=GENRE_CHOICES, default="other")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("title",)
        indexes = [
            models.Index(fields=["isbn"]),
            models.Index(fields=["genre"]),
        ]

    def __str__(self):
        return self.title

    @property
    def author_names(self):
        """Get comma-separated list of author names"""
        return ", ".join([author.name for author in self.authors.all()])


class Author(models.Model):
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(blank=True, null=True)
    death_date = models.DateField(blank=True, null=True)
    website = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name
