from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from reviews.constants import (USERNAME_REGEX,
                               USERNAME_MAX_LENGTH,
                               EMAIL_MAX_LENGTH,
                               ROLE_NAME_MAX_LENGTH)


class User(AbstractUser):
    """Расширенная модель юзера с дополнительными полями role и bio."""

    class Role(models.TextChoices):
        USER = 'user', _('User')
        MODERATOR = 'moderator', _('Moderator')
        ADMIN = 'admin', _('Admin')

    role = models.CharField(
        verbose_name='Роль',
        max_length=ROLE_NAME_MAX_LENGTH,
        choices=Role.choices,
        default=Role.USER,
    )
    username = models.CharField(
        verbose_name='Никнейм',
        null=False,
        unique=True,
        max_length=USERNAME_MAX_LENGTH,
        validators=[RegexValidator(
            regex=USERNAME_REGEX,
            message='Unacceptable symbol'
        )]
    )
    email = models.EmailField(verbose_name='Почта',
                              blank=False,
                              null=False,
                              unique=True,
                              max_length=EMAIL_MAX_LENGTH)
    bio = models.TextField(verbose_name='О себе',
                           blank=True)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['-date_joined']

    def __str__(self):
        return self.username

    @property
    def is_moderator(self):
        return self.role == self.Role.MODERATOR

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def clean(self):
        """Проверка, что username не равен 'me' (тольк. нижний регистр)."""
        if self.username == 'me':
            raise ValidationError('Username "me" is not allowed.')

    def save(self, *args, **kwargs):
        """Переопределяем метод save, чтобы вызвать метод clean."""
        self.clean()
        super(User, self).save(*args, **kwargs)
