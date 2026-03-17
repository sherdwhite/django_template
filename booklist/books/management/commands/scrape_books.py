"""
Scrape book data from the Open Library API and generate a Django fixture JSON file.

Usage:
    python manage.py scrape_books
    python manage.py scrape_books --output books/fixtures/scraped_books.json
    python manage.py scrape_books --per-author 15
    python manage.py scrape_books --no-descriptions  # skip fetching descriptions (faster)
"""

import json
import logging
import time
import urllib.parse
import urllib.request
from pathlib import Path

from django.core.management import BaseCommand
from django.utils import timezone

logger = logging.getLogger(__name__)

# Authors to search for and their default genre mapping
AUTHORS = [
    ("Stephen King", "fiction"),
    ("Lois McMaster Bujold", "sci_fi"),
    ("Robert Jordan", "fantasy"),
    ("J.R.R. Tolkien", "fantasy"),
    ("Isaac Asimov", "sci_fi"),
    ("Ursula K. Le Guin", "sci_fi"),
    ("Frank Herbert", "sci_fi"),
    ("Terry Pratchett", "fantasy"),
    ("Brandon Sanderson", "fantasy"),
    ("Neil Gaiman", "fantasy"),
]

DEFAULT_PER_AUTHOR = 10
OPEN_LIBRARY_SEARCH_URL = "https://openlibrary.org/search.json"
OPEN_LIBRARY_WORKS_URL = "https://openlibrary.org"
REQUEST_DELAY = 1  # seconds between API requests


def fetch_json(url):
    """Fetch JSON from a URL with a polite User-Agent header."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "BookListApp/1.0 (Django fixture generator)"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode())


def fetch_description(work_key):
    """Fetch the description for a work from Open Library's works endpoint."""
    try:
        url = f"{OPEN_LIBRARY_WORKS_URL}{work_key}.json"
        data = fetch_json(url)
        desc = data.get("description", "")
        # Description can be a string or a dict with a "value" key
        if isinstance(desc, dict):
            desc = desc.get("value", "")
        return desc
    except Exception as e:
        logger.debug("Could not fetch description for %s: %s", work_key, e)
        return ""


class Command(BaseCommand):
    help = "Scrape book data from Open Library API and generate a fixture JSON file"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="books/fixtures/scraped_books.json",
            help="Output file path for the fixture JSON (default: books/fixtures/scraped_books.json)",
        )
        parser.add_argument(
            "--per-author",
            type=int,
            default=DEFAULT_PER_AUTHOR,
            help=f"Max number of books to fetch per author (default: {DEFAULT_PER_AUTHOR})",
        )
        parser.add_argument(
            "--no-descriptions",
            action="store_true",
            help="Skip fetching descriptions (faster, but books will have empty descriptions)",
        )

    def handle(self, *args, **options):
        output_path = Path(options["output"])
        per_author = options["per_author"]
        skip_descriptions = options["no_descriptions"]

        fixtures = []
        author_map = {}  # author name -> pk
        author_pk = 1
        book_pk = 1
        seen_isbns = set()
        seen_titles = set()
        now = timezone.now().isoformat()

        for author_search_name, default_genre in AUTHORS:
            self.stdout.write(f"Searching for books by {author_search_name}...")

            params = urllib.parse.urlencode(
                {
                    "author": author_search_name,
                    "limit": per_author
                    * 3,  # request extra since some won't have ISBNs
                    "fields": ",".join(
                        [
                            "title",
                            "author_name",
                            "isbn",
                            "first_publish_year",
                            "number_of_pages_median",
                            "language",
                            "subject",
                            "key",
                        ]
                    ),
                    "sort": "rating",
                }
            )
            url = f"{OPEN_LIBRARY_SEARCH_URL}?{params}"

            try:
                data = fetch_json(url)
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"  Error fetching: {e}"))
                continue

            count = 0
            for doc in data.get("docs", []):
                if count >= per_author:
                    break

                title = doc.get("title", "").strip()
                isbns = doc.get("isbn", [])
                if not title or not isbns:
                    continue

                # Skip duplicate titles (different editions of same book)
                title_lower = title.lower()
                if title_lower in seen_titles:
                    continue

                # Pick first valid ISBN that we haven't seen
                isbn = None
                for candidate in isbns:
                    clean = candidate.replace("-", "").strip()
                    if clean and clean not in seen_isbns and len(clean) in (10, 13):
                        isbn = clean
                        break
                if not isbn:
                    continue

                seen_isbns.add(isbn)
                seen_titles.add(title_lower)

                # --- Authors ---
                author_names = doc.get("author_name", [author_search_name])
                author_pks = []
                for name in author_names:
                    name = name.strip()[:255]
                    if name not in author_map:
                        author_map[name] = author_pk
                        fixtures.append(
                            {
                                "model": "books.author",
                                "pk": author_pk,
                                "fields": {
                                    "name": name,
                                    "bio": "",
                                    "website": "",
                                    "created_at": now,
                                },
                            }
                        )
                        author_pk += 1
                    author_pks.append(author_map[name])

                # --- Description ---
                description = ""
                if not skip_descriptions:
                    work_key = doc.get("key", "")
                    if work_key:
                        description = fetch_description(work_key)
                        time.sleep(0.5)  # rate limit for description requests

                # --- Book fields ---
                book_fields = {
                    "title": title[:255],
                    "description": description,
                    "isbn": isbn,
                    "authors": author_pks,
                    "genre": default_genre,
                    "language": "en",
                    "created_at": now,
                    "updated_at": now,
                }

                # Optional fields
                pub_year = doc.get("first_publish_year")
                if pub_year:
                    book_fields["publication_date"] = f"{pub_year}-01-01"

                page_count = doc.get("number_of_pages_median")
                if page_count and page_count > 0:
                    book_fields["page_count"] = page_count

                fixtures.append(
                    {
                        "model": "books.book",
                        "pk": book_pk,
                        "fields": book_fields,
                    }
                )
                book_pk += 1
                count += 1

            self.stdout.write(f"  Found {count} books by {author_search_name}")
            time.sleep(REQUEST_DELAY)

        # Write out the fixture file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            json.dump(fixtures, f, indent=2, ensure_ascii=False)

        total_books = book_pk - 1
        total_authors = author_pk - 1
        self.stdout.write(
            self.style.SUCCESS(
                f"\nGenerated fixture: {output_path}\n"
                f"  {total_books} books, {total_authors} authors"
            )
        )
        self.stdout.write(
            f"\nLoad it with: python manage.py loaddata {output_path.name}"
        )
