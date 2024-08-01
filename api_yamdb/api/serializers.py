from reviews.models import Category, Genre, Title

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
        fields = ('id', 'name', 'year',
                #   'rating',  раскоменчу после задачи Руслана
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
