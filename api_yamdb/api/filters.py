import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """
    Фильтрация по полям модели Title.
    Во вью необходимо вместо
    filterset_fields использовать filterset_class.
    """
    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    year = django_filters.NumberFilter(
        field_name='year',
    )
    genre = django_filters.CharFilter(
        field_name='genre__slug',
    )
    category = django_filters.CharFilter(
        field_name='category__slug',
    )

    class Meta:
        model = Title
        fields = ('name', 'year', 'category', 'genre')
