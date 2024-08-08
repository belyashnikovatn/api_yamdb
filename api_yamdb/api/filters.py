import django_filters

from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """
    Фильтрация по полям модели Title.

    Этот фильтр позволяет фильтровать объекты модели Title
    по следующим полям: name, year, genre и category.

    Атрибуты
    --------
        name : Фильтр по названию, ищет подстроку в поле name.
        genre : Фильтр по жанру, ищет по slug жанра.
        category : Фильтр по категории, ищет по slug категории.
    """

    name = django_filters.CharFilter(
        field_name='name',
        lookup_expr='icontains'
    )
    genre = django_filters.CharFilter(
        field_name='genre__slug',
    )
    category = django_filters.CharFilter(
        field_name='category__slug',
    )

    class Meta:
        """
        Метакласс для настройки фильтрации.

        Атрибуты
        --------
            model : Модель, для которой применяется фильтр (Title).
            fields : Поля, по которым будет происходить фильтрация.
        """

        model = Title
        fields = ('name', 'year', 'category', 'genre')
