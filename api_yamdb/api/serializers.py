from reviews.models import Category, Genre, Title

from rest_framework import serializers


class GenreSerailizer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class CategorySerailizer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ('name', 'slug')


class TitleReadOnlySerailizer(serializers.ModelSerializer):
    genre = GenreSerailizer(many=True, read_only=True)
    category = CategorySerailizer(read_only=True)
    rating = 0

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating',
                  'description', 'genre', 'category')


class TitleSerailizer(TitleReadOnlySerailizer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
