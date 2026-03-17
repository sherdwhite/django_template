from django.contrib import admin

from .models import Author, Book


class AuthorInline(admin.TabularInline):
    model = Book.authors.through
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "author_names",
        "genre",
        "isbn",
    ]
    list_filter = ["genre", "publication_date", "language"]
    search_fields = ["title", "isbn", "authors__name"]
    readonly_fields = ["created_at", "updated_at"]
    filter_horizontal = ["authors"]

    fieldsets = (
        ("Basic Info", {"fields": ("title", "authors", "description")}),
        (
            "Publication Details",
            {"fields": ("isbn", "publication_date", "page_count", "language", "genre")},
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ["name", "birth_date", "created_at"]
    search_fields = ["name", "bio"]
    readonly_fields = ["created_at"]
