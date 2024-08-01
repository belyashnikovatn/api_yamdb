from rest_framework import viewsets
from rest_framework import filters, mixins, viewsets
from reviews.models import Title, Genre, Category
from api.serializers import (
    GenreSerailizer,
    CategorySerailizer,
    TitleSerailizer,
    TitleReadOnlySerailizer
)
from django_filters.rest_framework import DjangoFilterBackend


class NameSlugModelViewSet(mixins.CreateModelMixin,
                           mixins.ListModelMixin,
                           mixins.DestroyModelMixin,
                           viewsets.GenericViewSet):
    """Абстрактный класс для вьюсетов категория/жанр."""
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(NameSlugModelViewSet):
    """Вьюсет для жанра."""
    serializer_class = GenreSerailizer
    queryset = Genre.objects.all()


class CategoryViewSet(NameSlugModelViewSet):
    """Вьюсет для категории."""
    serializer_class = CategorySerailizer
    queryset = Category.objects.all()


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для произведений."""
    serializer_class = TitleSerailizer
    queryset = Title.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('name', 'year', 'genre__slug', 'category__slug')

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return TitleReadOnlySerailizer
        return TitleSerailizer
