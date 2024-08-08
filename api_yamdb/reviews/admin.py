from django.contrib import admin

from reviews.models import Category, Comment, Genre, Review, Title


class DisplayModelAdmin(admin.ModelAdmin):
    """Custom base for all classes."""

    def __init__(self, model, admin_site):
        """For the list display."""
        self.list_display = [
            field.name for field in model._meta.fields if field.name != 'id'
        ]
        super().__init__(model, admin_site)


@admin.register(Category)
class CategoryAdmin(DisplayModelAdmin):
    """Admin Category."""


@admin.register(Genre)
class GenreAdmin(DisplayModelAdmin):
    """Admin Genre."""


@admin.register(Title)
class TitleAdmin(DisplayModelAdmin):
    """Admin Title."""

    list_editable = (
        'category',
    )
    list_display = ('name', 'genres', 'category', 'year', 'description')

    def genres(self, obj):
        title_genres = obj.genres.all()
        return ' , '.join(x.name for x in title_genres)


@admin.register(Review)
class ReviewAdmin(DisplayModelAdmin):
    """Admin Review."""


@admin.register(Comment)
class CommentAdmin(DisplayModelAdmin):
    """Admin Comment."""
