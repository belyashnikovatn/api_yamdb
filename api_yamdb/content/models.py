from datetime import datetime

from django.contrib.auth import get_user_model
from django.core.validators import (
    MinValueValidator,
    MaxValueValidator,
    RegexValidator
)
from django.db import models


User = get_user_model()


class Detail(models.Model):
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

    def __str__(self):
        return self.name


class Genre(Detail):
    """Класс модели данных для жанров."""

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)


class Category(Detail):
    """Класс модели данных для категорий."""

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)


class Title(models.Model):
    """Класс модели данных для произведений."""
    name = models.CharField('Название', max_length=256)
    year = models.PositiveIntegerField(
        'Год выпуска',
        validators=[
            MinValueValidator(
                1895,
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
        return f'{self.name}, {self.year}'


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
        return f'{self.genre} у {self.title}'


class Review(models.Model):
    """Класс модели данных для отзывов."""
    text = models.TextField('Текст отзыва')
    score = models.PositiveIntegerField(
        'Оценка',
        validators=[
            MinValueValidator(1, message='More'),
            MaxValueValidator(10, message='Less')
        ]
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации, автоматически',
        auto_now_add=True,
        db_index=True
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Произведение'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)
        constraints = (
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review'
            ),
        )

    def __str__(self):
        return f'{self.title__name}, {self.score}'


class Comment(models.Model):
    """Класс модели данных для комментариев."""
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор'
    )
    text = models.TextField('Текст комментария')
    pub_date = models.DateTimeField(
        verbose_name='Дата и время публикации, автоматически',
        auto_now_add=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text[:50]
