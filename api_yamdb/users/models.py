from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Класс модели данных для пользователей, кастомизация стандратного класса."""
    bio = models.TextField('Биография', blank=True)