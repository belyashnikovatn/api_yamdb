from rest_framework import serializers

from django.contrib.auth.tokens import default_token_generator as dtg
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from api.validators import validate_data
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class SignUpSerializer(serializers.Serializer):

    """
    Класс-сериализатор для регистрации пользователей.
    Проверяет уникальность email и username.
    """

    email = serializers.EmailField(max_length=254)
    username = serializers.CharField(max_length=150)

    def validate(self, data):
        return validate_data(data)


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
    rating = serializers.FloatField(read_only=True)

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
        allow_null=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def to_representation(self, value):
        representation = super().to_representation(value)
        title_genres = Genre.objects.filter(slug__in=representation['genre'])
        representation['genre'] = title_genres.values('name', 'slug')
        category = get_object_or_404(Category, slug=representation['category'])
        title_category = {'name': category.name, 'slug': category.slug}
        representation['category'] = title_category
        return representation


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

    def validate_score(self, value):
        if not (0 <= value <= 10):
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
        fields = '__all__'
