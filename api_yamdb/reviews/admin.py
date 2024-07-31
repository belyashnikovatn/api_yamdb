from django.contrib import admin

from reviews.models import Category, Genre, Title


class CustomModelAdmin(admin.ModelAdmin):
    """Custom base for all classes."""

    def __init__(self, model, admin_site):
        """For the list display."""
        self.list_display = [
            field.name for field in model._meta.fields if field.name != 'id'
        ]
        super(CustomModelAdmin, self).__init__(model, admin_site)


@admin.register(Category)
class CategoryAdmin(CustomModelAdmin):
    """Admin Category."""


@admin.register(Genre)
class GenreAdmin(CustomModelAdmin):
    """Admin Genre."""


@admin.register(Title)
class TitleAdmin(CustomModelAdmin):
    """Admin Title."""
