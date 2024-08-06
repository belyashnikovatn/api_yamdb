from django.db.models import Avg
from rest_framework import serializers
from django.contrib.auth.tokens import default_token_generator as dtg
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from reviews.models import Category, Comment, Genre, Title, Review
from users.models import User
from reviews.models import Category, Genre, Title
from users.models import User
from django.core.validators import RegexValidator


class SignUpSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150,
                                     validators=[RegexValidator(
                                         regex=r'^[\w.@+-]+\Z',
                                         message="Юзернейм должен содержать только буквы, цифры и символы: . @ + - _")])
    """
    Класс-сериализатор для регистрации пользователей.
    Проверяет уникальность email и username.
    """
    class Meta:
        model = User
        fields = ('email', 'username',)

    def validate_username(self, value):
        """
        Проверяет, что username не равен 'me'.
        """
        if value.lower() == 'me':
            raise serializers.ValidationError("Юзернейм 'me' недопустим.")
        return value


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
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        if obj.reviews.count() == 0:
            return None
        review_aggregate = (obj.reviews.aggregate(rating=Avg('score')))
        return review_aggregate['rating']

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')


class TitleSerializer(serializers.ModelSerializer):
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


class ReviewSerializer(serializers.ModelSerializer):
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    def validate_score(self, value):
        if not (1 <= value <= 10):
            raise serializers.ValidationError('Оценка по 10-бальной шкале!')
        return value

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Может существовать только один отзыв!')
        return data

    class Meta:
        model = Review
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Comment
        fields = '__all__'
