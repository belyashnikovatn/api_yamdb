from datetime import datetime

from django.db import models


class Genre(models.Model):
    """Класс модели данных для жанров."""
    name = models.CharField('Название', max_length=256)
    slug = models.SlugField('slug', unique=True, max_length=50)

    class Meta:
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Класс модели данных для категорий."""
    name = models.CharField('Название', max_length=256)
    slug = models.SlugField('slug', unique=True, max_length=50)

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Title(models.Model):
    """Класс модели данных для произведений."""
    name = models.CharField('Название', max_length=256)
    year = models.PositiveIntegerField('Год выпуска',)
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
    score = models.PositiveIntegerField('Оценка'),
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
