from reviews.models import Category, Comment, Genre, Title, Review
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework import serializers


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
        fields = '__all__'
        model = Review


class CommentSerializer(serializers.ModelSerializer):
    review = serializers.PrimaryKeyRelatedField(
        queryset=Review.objects.all(),
        read_only=True
    )
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        fields = '__all__'
        model = Comment
