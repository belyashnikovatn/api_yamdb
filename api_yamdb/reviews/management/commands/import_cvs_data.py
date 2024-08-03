from django.core.management.base import BaseCommand, CommandError
from reviews.models import Genre, Category, Title


class Command(BaseCommand):
    """Класс для кастомной команды."""

    help = 'Import cvs-files into DB through models.'

    def handle(self, *args, **options):
        print('Hi!')
