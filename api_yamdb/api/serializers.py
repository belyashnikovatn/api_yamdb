from rest_framework import serializers

from django.contrib.auth.tokens import default_token_generator as dtg
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from api.validators import validate_data
from reviews.models import Category, Comment, Genre, Review, Title
from reviews.constants import (EMAIL_MAX_LENGTH,
                               USERNAME_MAX_LENGTH,
                               CONFIRMATION_CODE_MAX_LENGTH)
from users.models import User
from reviews.constants import (
    MAX_SERIALIZER_SCORE, MIN_SERIALIZER_SCORE
)


class SignUpSerializer(serializers.Serializer):
    """Проверка уникальности email и username."""

    email = serializers.EmailField(max_length=EMAIL_MAX_LENGTH)
    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)

    def validate(self, data):
        return validate_data(data)


class TokenSerializer(serializers.Serializer):
    """
    Класс-сериализатор для получения токена JWT.

    Проверяет корректность username и кода подтверждения.
    Наследуем от класса Serializer, а не ModelSerializer, так как:
    1. не требуется создавать или обновлять объекты модели.
    2. требуется только проводить валидацию переданных значений.

    Атрибуты
    --------
    username : Имя зарегестрированного пользователя, который получает токен.
    confirmation_code : Код, полученный пользователем на email.

    Методы
    ------
    validate(data (dict)) : Проверка корректности username и confirmation_code.
    """

    username = serializers.CharField(max_length=USERNAME_MAX_LENGTH)
    confirmation_code = serializers.CharField(
        max_length=CONFIRMATION_CODE_MAX_LENGTH)

    class Meta:
        """
        Метакласс для настройки сериализатора.

        Атрибуты
        --------
        model : Модель, для которой применяется сериализатор (User).
        fields : Поля, по которым будет происходить сериализация.
        """

        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, data):
        """Валидирует data и возращает провалидированный словарь data."""
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if not dtg.check_token(user, confirmation_code):
            raise serializers.ValidationError('Неверный код подтверждения')
        return data


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для переопределенной модели Пользователя."""

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name',
                  'last_name', 'bio', 'role']


class GenreSerializer(serializers.ModelSerializer):
    """Класс-сериализатор для жанра."""

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class CategorySerializer(serializers.ModelSerializer):
    """Класс-сериализатор для категории."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleReadOnlySerializer(serializers.ModelSerializer):
    """Класс-сериализатор для произведений: метод get."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')


class TitleSerializer(serializers.ModelSerializer):
    """Класс-сериализатор для произведений: методы кроме get."""

    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True,
        required=True,
        allow_null=False,
        allow_empty=False
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def to_representation(self, instance):
        return TitleReadOnlySerializer(instance).data


class ReviewSerializer(serializers.ModelSerializer):
    """Класс-сериализатор для ревью."""

    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ['title', 'id', 'text', 'author', 'score', 'pub_date']

    def validate_score(self, value):
        if not (MIN_SERIALIZER_SCORE <= value <= MAX_SERIALIZER_SCORE):
            raise serializers.ValidationError(
                f'Оценка должна быть в диапазоне от '
                f'{MIN_SERIALIZER_SCORE} до '
                f'{MAX_SERIALIZER_SCORE}!'
            )
        return value

    def validate(self, data):
        request = self.context['request']

        if request.method == 'POST':
            author = request.user
            title_id = self.context.get('view').kwargs.get('title_id')
            title = get_object_or_404(Title, pk=title_id)

            if Review.objects.filter(title=title, author=author).exists():
                raise ValidationError('Может существовать только один отзыв!')

        return data


class CommentSerializer(serializers.ModelSerializer):
    """Класс-сериализатор для комментариев."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )
    review = serializers.SlugRelatedField(
        slug_field='text',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date', 'review')
