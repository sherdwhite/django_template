# -*- coding: utf-8 -*-

from django.db.models import Q
from django.views import generic

from .models import Book


class MainView(generic.TemplateView):
    template_name = "main.html"


class BookListView(generic.ListView):
    model = Book
    template_name = "books/book_list.html"
    context_object_name = "books"
    paginate_by = 12

    def get_queryset(self):
        queryset = Book.objects.prefetch_related("authors")

        search = self.request.GET.get("search", "").strip()
        genre = self.request.GET.get("genre", "").strip()

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(authors__name__icontains=search)
                | Q(isbn__icontains=search)
            ).distinct()

        if genre:
            queryset = queryset.filter(genre=genre)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["search_query"] = self.request.GET.get("search", "")
        context["genre_filter"] = self.request.GET.get("genre", "")
        context["genre_choices"] = Book.GENRE_CHOICES
        return context
