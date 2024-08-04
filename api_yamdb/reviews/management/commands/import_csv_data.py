import csv
import os
import logging

from django.conf import settings
from django.core.management.base import BaseCommand

from api_yamdb.settings import CSV_FILES_DIRS
from reviews.models import (
    Category,
    Genre,
    GenreTitle,
    NameSlugModel,
    Title,
    Review
)
from users.models import User


logging.basicConfig(
    format='%(asctime)s - %(funcName)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

# словарь для ссылок на объекты моделей
FKEYS = {
    'category': ('category', Category),
    'author': ('author', User),
}


def clean(model_name):
    """Удаляет данные из таблиц, чтобы не было ошибок на дубли итд."""
    try:
        model_name.objects.all().delete()
        logging.info(f'Данные из таблицы {model_name} удалены.')
    except Exception as error:
        logging.error(f'Ошибка {error}!')


def load(csv_file, model):
    """Загружает данные из файла через модель."""
    with open(os.path.join(CSV_FILES_DIRS, csv_file),
              encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        try:
            for row in reader:
                # проверка на ссылку на объект
                if (k := set(row.keys()) & set(FKEYS)):
                    for i in list(k):
                        row[i] = FKEYS[i][1].objects.get(pk=row[i])
                entity = model(**row)
                entity.save()
            logging.info(f'Данные "{csv_file}" загружены.')
        except Exception as error:
            logging.error(f'Ошибка {error}! Смотри {row.keys()}')


class Command(BaseCommand):
    """Класс для кастомной команды."""

    help = 'Import csv-files into DB through models.'

    def handle(self, *args, **options):
        # Clean the tables before.
        tables_to_clean = [NameSlugModel, GenreTitle, Review, Title, User]
        [clean(table) for table in tables_to_clean]

        # Import data into cleaned tables through ORM.
        files_models = {
            'category.csv': Category,
            'genre.csv': Genre,
            'titles.csv': Title,
            'genre_title.csv': GenreTitle,
            'users.csv': User,
            'review.csv': Review,
        }
        [load(csv_file, model) for csv_file, model in files_models.items()]
