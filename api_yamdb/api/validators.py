import re

from django.db.models import Q
from rest_framework import serializers

from reviews.constants import USERNAME_REGEX
from users.models import User


def validate_data(data):
    """Валидации полученых значений username и email."""

    username = data.get('username')
    email = data.get('email')

    if username and email:

        if not re.match(USERNAME_REGEX, username):
            raise serializers.ValidationError('Check username')
        if username == 'me':
            raise serializers.ValidationError('Username "me" not allowed')

        if (User.objects.filter(
                Q(email__iexact=email) & ~Q(username__iexact=username))):
            raise serializers.ValidationError('This email is taken')

        if (User.objects.filter(
                Q(username__iexact=username) & ~Q(email__iexact=email))):
            raise serializers.ValidationError('This username is taken')

    return data
