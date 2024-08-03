from datetime import datetime
from reviews.constants import SLICELENGTH, MINYEAR

from django.contrib.auth import get_user_model
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    RegexValidator
)
from django.db import models


User = get_user_model()


class NameSlugModel(models.Model):
    """Абстрактный класс для категории и жанра."""
    name = models.CharField('Название', max_length=256)
    slug = models.SlugField(
        'slug',
        unique=True,
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[-a-zA-Z0-9_]+$',
                message='Unacceptable slug'
            )
        ]
    )

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name[:SLICELENGTH]


class Genre(NameSlugModel):
    """Класс модели данных для жанров."""

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Category(NameSlugModel):
    """Класс модели данных для категорий."""

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    """Класс модели данных для произведений."""
    name = models.CharField('Название', max_length=256)
    year = models.PositiveIntegerField(
        'Год выпуска',
        validators=[
            MinValueValidator(
                MINYEAR,
                message='This is not possible!'),
            MaxValueValidator(
                int(datetime.now().year),
                message='This is not possible!'
            )
        ]
    )
    description = models.TextField('Описание')
    genre = models.ManyToManyField(
        Genre,
        through='GenreTitle',
        related_name='titles',
        verbose_name='Жанр(ы)'
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        verbose_name='Категория'
    )

    class Meta:
        verbose_name = 'произведения'
        verbose_name_plural = 'Произведение'
        ordering = ('name', '-year')

    def __str__(self):
        return f'{self.name[:SLICELENGTH]}, {self.year}'


class GenreTitle(models.Model):
    """Класс модели данных для жанров конкретных произведений."""
    title = models.ForeignKey(Title, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'жанр произведения'
        verbose_name_plural = 'Жанры произведений'
        ordering = ('id',)
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'genre'],
                name='unique_title_genre'
            )
        ]

    def __str__(self):
        return f'{self.genre} у {self.title[:SLICELENGTH]}'


class AuthorTextPubDateBaseModel(models.Model):
    """Вспомогательный класс, связывающий отзывы и комментарии к ним."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='texts',
        verbose_name='Автор'
    )
    text = models.TextField(verbose_name='Текст')
    pub_date = models.DateTimeField(
        verbose_name='Дата добавления',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        abstract = True
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:SLICELENGTH]


class Review(AuthorTextPubDateBaseModel):
    """Модель для отзыва."""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.PositiveSmallIntegerField(
        verbose_name='Оценка',
        validators=[
            MinValueValidator(
                1,
                message='Введенная оценка ниже допустимой'
            ),
            MaxValueValidator(
                10,
                message='Введенная оценка выше допустимой'
            ),
        ]
    )

    class Meta(AuthorTextPubDateBaseModel.Meta):
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        default_related_name = 'reviews'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='unique_review'
            )
        ]


class Comment(AuthorTextPubDateBaseModel):
    """Модель для представления комментария к посту."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )

    class Meta(AuthorTextPubDateBaseModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        default_related_name = 'comments'
