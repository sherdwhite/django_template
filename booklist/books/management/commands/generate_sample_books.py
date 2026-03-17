# -*- coding: utf-8 -*-

import random
from datetime import date

from django.core.management.base import BaseCommand

from books.models import Author, Book, Publisher

SAMPLE_AUTHORS = [
    {"name": "Jane Austen", "birth_date": "1775-12-16", "death_date": "1817-07-18"},
    {"name": "Mark Twain", "birth_date": "1835-11-30", "death_date": "1910-04-21"},
    {"name": "George Orwell", "birth_date": "1903-06-25", "death_date": "1950-01-21"},
    {"name": "Virginia Woolf", "birth_date": "1882-01-25", "death_date": "1941-03-28"},
    {
        "name": "Ernest Hemingway",
        "birth_date": "1899-07-21",
        "death_date": "1961-07-02",
    },
    {"name": "Toni Morrison", "birth_date": "1931-02-18", "death_date": "2019-08-05"},
    {
        "name": "Gabriel García Márquez",
        "birth_date": "1927-03-06",
        "death_date": "2014-04-17",
    },
    {"name": "Haruki Murakami", "birth_date": "1949-01-12"},
    {"name": "Chimamanda Ngozi Adichie", "birth_date": "1977-09-15"},
    {"name": "Neil Gaiman", "birth_date": "1960-11-10"},
    {"name": "Isaac Asimov", "birth_date": "1920-01-02", "death_date": "1992-04-06"},
    {
        "name": "Ursula K. Le Guin",
        "birth_date": "1929-10-21",
        "death_date": "2018-01-22",
    },
    {"name": "Margaret Atwood", "birth_date": "1939-11-18"},
    {"name": "Ray Bradbury", "birth_date": "1920-08-22", "death_date": "2012-06-05"},
    {"name": "Kurt Vonnegut", "birth_date": "1922-11-11", "death_date": "2007-04-11"},
]

SAMPLE_PUBLISHERS = [
    {"name": "Penguin Books"},
    {"name": "HarperCollins"},
    {"name": "Random House"},
    {"name": "Simon & Schuster"},
    {"name": "Macmillan Publishers"},
    {"name": "Hachette Book Group"},
    {"name": "Oxford University Press"},
    {"name": "Vintage Books"},
]

# (title, genre, description, author_indices)
SAMPLE_BOOKS = [
    (
        "Pride and Prejudice",
        "romance",
        "A witty exploration of love, reputation, and class in Regency-era England.",
        [0],
    ),
    (
        "Sense and Sensibility",
        "romance",
        "Two sisters navigate love and heartbreak with contrasting temperaments.",
        [0],
    ),
    (
        "Adventures of Huckleberry Finn",
        "fiction",
        "A boy and a runaway slave journey down the Mississippi River.",
        [1],
    ),
    (
        "The Adventures of Tom Sawyer",
        "fiction",
        "A mischievous boy's adventures in a small Missouri town.",
        [1],
    ),
    (
        "1984",
        "sci_fi",
        "A dystopian novel set in a totalitarian society under constant surveillance.",
        [2],
    ),
    (
        "Animal Farm",
        "fiction",
        "An allegorical novella reflecting events leading to the Russian Revolution.",
        [2],
    ),
    (
        "Mrs Dalloway",
        "fiction",
        "A day in the life of Clarissa Dalloway as she prepares for a party.",
        [3],
    ),
    (
        "To the Lighthouse",
        "fiction",
        "A family's visits to the Isle of Skye between 1910 and 1920.",
        [3],
    ),
    (
        "The Old Man and the Sea",
        "fiction",
        "An aging fisherman's epic struggle with a giant marlin.",
        [4],
    ),
    (
        "A Farewell to Arms",
        "fiction",
        "An American ambulance driver in the Italian army during World War I.",
        [4],
    ),
    (
        "Beloved",
        "fiction",
        "A formerly enslaved woman is haunted by the ghost of her dead daughter.",
        [5],
    ),
    (
        "Song of Solomon",
        "fiction",
        "A young man's journey of self-discovery through his family's history.",
        [5],
    ),
    (
        "One Hundred Years of Solitude",
        "fiction",
        "The multi-generational story of the Buendía family in Macondo.",
        [6],
    ),
    (
        "Love in the Time of Cholera",
        "romance",
        "A love story spanning over fifty years in a Caribbean city.",
        [6],
    ),
    (
        "Norwegian Wood",
        "fiction",
        "A nostalgic story of loss and sexuality in 1960s Japan.",
        [7],
    ),
    (
        "Kafka on the Shore",
        "fantasy",
        "Two intertwining stories exploring fate and consciousness.",
        [7],
    ),
    (
        "Americanah",
        "fiction",
        "A young Nigerian woman's experiences with race and identity in America.",
        [8],
    ),
    (
        "Half of a Yellow Sun",
        "history",
        "The Nigerian Civil War through the eyes of three characters.",
        [8],
    ),
    (
        "American Gods",
        "fantasy",
        "A recently released convict discovers a hidden world of gods.",
        [9],
    ),
    (
        "Coraline",
        "children",
        "A young girl discovers a parallel world behind a mysterious door.",
        [9],
    ),
    (
        "Foundation",
        "sci_fi",
        "A mathematician predicts the fall of a galactic empire and plans for renewal.",
        [10],
    ),
    (
        "I, Robot",
        "sci_fi",
        "Nine stories explore the interaction of humans and robots.",
        [10],
    ),
    (
        "The Left Hand of Darkness",
        "sci_fi",
        "An envoy visits a planet whose inhabitants have no fixed gender.",
        [11],
    ),
    (
        "A Wizard of Earthsea",
        "fantasy",
        "A young wizard must face the shadow he has unleashed on the world.",
        [11],
    ),
    (
        "The Handmaid's Tale",
        "sci_fi",
        "A dystopian novel set in a totalitarian theocratic state.",
        [12],
    ),
    (
        "Oryx and Crake",
        "sci_fi",
        "A post-apocalyptic novel about genetic engineering gone wrong.",
        [12],
    ),
    (
        "Fahrenheit 451",
        "sci_fi",
        "A future society where books are banned and firemen burn them.",
        [13],
    ),
    (
        "The Martian Chronicles",
        "sci_fi",
        "Humanity's colonization of Mars over many years.",
        [13],
    ),
    (
        "Slaughterhouse-Five",
        "sci_fi",
        "A soldier becomes unstuck in time after surviving the bombing of Dresden.",
        [14],
    ),
    (
        "Cat's Cradle",
        "sci_fi",
        "A satirical novel exploring science, technology, and religion.",
        [14],
    ),
    (
        "The Great Gatsby",
        "fiction",
        "The story of the mysteriously wealthy Jay Gatsby and his love for Daisy.",
        [1, 4],
    ),
    (
        "Brave New World",
        "sci_fi",
        "A futuristic society driven by technology, conditioning, and pleasure.",
        [2, 13],
    ),
]


def _generate_isbn():
    """Generate a random 13-digit ISBN."""
    prefix = random.choice(["978", "979"])
    body = "".join([str(random.randint(0, 9)) for _ in range(9)])
    return f"{prefix}{body}{random.randint(0, 9)}"


class Command(BaseCommand):
    help = "Generate sample books, authors, and publishers for development."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing books, authors, and publishers before generating.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            Book.objects.all().delete()
            Author.objects.all().delete()
            Publisher.objects.all().delete()
            self.stdout.write(self.style.WARNING("Cleared all existing data."))

        # Create publishers
        publishers = []
        for data in SAMPLE_PUBLISHERS:
            pub, created = Publisher.objects.get_or_create(name=data["name"])
            publishers.append(pub)
            if created:
                self.stdout.write(f"  Created publisher: {pub.name}")

        # Create authors
        authors = []
        for data in SAMPLE_AUTHORS:
            author, created = Author.objects.get_or_create(
                name=data["name"],
                defaults={
                    "birth_date": data.get("birth_date"),
                    "death_date": data.get("death_date"),
                },
            )
            authors.append(author)
            if created:
                self.stdout.write(f"  Created author: {author.name}")

        # Create books
        created_count = 0
        for title, genre, description, author_indices in SAMPLE_BOOKS:
            isbn = _generate_isbn()
            if Book.objects.filter(title=title).exists():
                self.stdout.write(f"  Skipped (exists): {title}")
                continue

            book = Book.objects.create(
                title=title,
                genre=genre,
                description=description,
                isbn=isbn,
                publisher=random.choice(publishers),
                publication_date=date(
                    random.randint(1950, 2023), random.randint(1, 12), 1
                ),
                page_count=random.randint(150, 800),
                language="en",
            )
            book.authors.set([authors[i] for i in author_indices])
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created {created_count} books, "
                f"{len(publishers)} publishers, {len(authors)} authors."
            )
        )
