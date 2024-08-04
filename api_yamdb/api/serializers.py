from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator as dtg
from django.shortcuts import get_object_or_404

from reviews.models import Category, Genre, Title
from users.models import User


class SignUpSerializer(serializers.ModelSerializer):
    """
    Класс-сериализатор для регистрации пользователей.
    Проверяет уникальность email и username.
    """
    class Meta:
        model = User
        fields = ['email', 'username']

    def validate_username(self, value):
        """
        Проверяет, что username не равен 'me'.
        """
        if value.lower() == 'me':
            raise serializers.ValidationError("Юзернейм 'me' недопустим.")
        return value

    def validate(self, data):
        """
        Проверяет, что email и username уникальны.
        """
        email = data.get('email')
        username = data.get('username')

        if User.objects.filter(email=email, username=username).exists():
            return data
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Такой email уже существует.")
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError("Такой username уже существует.")

        return data


class TokenSerializer(serializers.Serializer):
    """
    Класс-сериализатор для получения токена JWT.
    Проверяет корректность username и кода подтверждения.

    Наследуем от сериализатора класса Serializer, а не модели, так как:
    - не требуется создавать или обновлять объекты модели.
    - требуется только проводить валидацию переданных значений.
    """
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField(max_length=100)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        user = get_object_or_404(User, username=username)
        if not dtg.check_token(user, confirmation_code):
            raise serializers.ValidationError('Неверный код подтверждения')
        return data


class UserSerializer(serializers.ModelSerializer):
    """
    Класс-сериализатор для переопределенной модели пользователя.

    Применяются валидации и ограничения, указанные в модели User.
    Дополнительные специфические валидации не треубуются.
    """
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name',
                  'last_name', 'bio', 'role']


class GenreSerailizer(serializers.ModelSerializer):
    """Класс-сериализатор для жанра."""

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class CategorySerailizer(serializers.ModelSerializer):
    """Класс-сериализатор для категории."""

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleReadOnlySerailizer(serializers.ModelSerializer):
    """Класс-сериализатор для произведений: метод get."""
    genre = GenreSerailizer(many=True, read_only=True)
    category = CategorySerailizer(read_only=True)
    # тут пока заглушка
    rating = 0

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')


class TitleSerailizer(serializers.ModelSerializer):
    """Класс-сериализатор для произведений: методы кроме get."""
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
