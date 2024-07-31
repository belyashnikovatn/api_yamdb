from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Класс модели данных для пользователей,
    кастомизация стандратного класса."""

    class Role(models.TextChoices):
        USER = 'user', _('User')
        MODERATOR = 'moderator', _('Moderator')
        ADMIN = 'admin', _('Admin')

    role = models.CharField(
        max_length=9,
        choices=Role.choices,
        default=Role.USER,
    )
    username = models.CharField(
        'Никнейм',
        unique=True,
        max_length=150,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+$',
            message='Unacceptable symbol'
        )]
    )
    email = models.EmailField('Почта', max_length=254)
    first_name = models.CharField('Имя', max_length=150, blank=True)
    last_name = models.CharField('Фамилия', max_length=150, blank=True)
    bio = models.TextField('О себе', blank=True)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('id',)

    def __str__(self):
        return self.username
