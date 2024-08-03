from rest_framework import serializers

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

        - param value: Значение поля username.
        """
        if value.lower() == 'me':
            raise serializers.ValidationError("Юзернейм 'me' недопустим.")
        return value

    def validate(self, data):
        """
        Проверяет, что email и username уникальны.

        - param data: Данные сериализатора.
        """
        email = data.get('email')
        username = data.get('username')

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

    def validate(self, data):
        """
        Проверяет наличие пользователя с
        заданным username и confirmation_code.

        - param data: Входные данные (username и confirmation_code).
        """
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')

        try:
            user = User.objects.get(username=username,
                                    confirmation_code=confirmation_code)
        except User.DoesNotExist:
            raise serializers.ValidationError('Неверное имя пользователя'
                                              ' или код подтверждения')

        # добавляем найденного пользователя в словарь data под ключом 'user'
        data['user'] = user

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
