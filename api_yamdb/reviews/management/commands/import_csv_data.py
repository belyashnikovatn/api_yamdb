import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand

from reviews.models import Genre, Category, Title, GenreTitle, NameSlugModel
from users.models import User


class Command(BaseCommand):
    """Класс для кастомной команды."""

    help = 'Import csv-files into DB through models.'

    def handle(self, *args, **options):
        # Clean tables before.
        NameSlugModel.objects.all().delete()
        Title.objects.all().delete()
        files_models = {
            'category.csv': Category,
            'genre.csv': Genre,
            # 'genre_title.csv': GenreTitle,
            # 'titles.csv': Title
        }

        for csv_file, model in files_models.items():
            with open(os.path.join(
                    settings.BASE_DIR,
                    'static/data/',
                    csv_file),
                    encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    model.objects.create(**row)

            self.stdout.write(self.style.SUCCESS(
                f'{model.name} data imported successfully from {csv_file}'
            ))
