from datetime import datetime
import re

from django.db.models import Q
from django.core.exceptions import ValidationError
from rest_framework import serializers

from reviews.constants import (
    FORBIDDEN_USERNAME,
    MIN_YEAR,
    USERNAME_REGEX,
)
from users.models import User


def validate_data(data):
    """Валидации полученых значений username и email."""

    username = data.get('username')
    email = data.get('email')

    if username and email:

        if not re.match(USERNAME_REGEX, username):
            raise serializers.ValidationError('Check username')
        if username == FORBIDDEN_USERNAME:
            raise serializers.ValidationError(
                f'Username "{FORBIDDEN_USERNAME}" not allowed')

        if (User.objects.filter(
                Q(email__iexact=email) & ~Q(username__iexact=username))):
            raise serializers.ValidationError('This email is taken')

        if (User.objects.filter(
                Q(username__iexact=username) & ~Q(email__iexact=email))):
            raise serializers.ValidationError('This username is taken')

    return data


def real_year(value):
    if int(datetime.now().year) <= value < MIN_YEAR:
        raise ValidationError(
            'Укажите верный год.'
        )
