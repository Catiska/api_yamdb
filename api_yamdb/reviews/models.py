from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.constraints import UniqueConstraint
from django.db import models


class Review(models.Model):
    """Модель отзыва на произведение."""
    text = models.CharField('Текст отзыва', max_length=500)
    score = models.IntegerField(
        'Оценка',
        validators=(
            MinValueValidator(1, 'Минимальная оценка - 1'),
            MaxValueValidator(10, 'Максимальная оценка - 10')
        )
    )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='reviews')
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='reviews')
    pub_date = models.DateTimeField('Дата публикации',
                                auto_now_add=True)

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('author', 'title'),
                name='unique review'
            )
        ]

    def __str__(self):
        return self.text[:30]


class Comment(models.Model):
    """Модель комментария к отзыву."""
    text = models.CharField('Текст комментария', max_length=200)
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    review = models.ForeignKey(Review,
                               on_delete=models.CASCADE,
                               related_name='comments')
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название категории')
    slug = models.SlugField(unique=True, max_length=50, verbose_name='Слаг категории')


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название жанра')
    slug = models.SlugField(unique=True, max_length=50, verbose_name='Слаг жанра')


class Title(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название произведения')
    year = models.DateTimeField(verbose_name='Дата')
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    category = models.ForeignKey(
        Category,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория'
    )
    description = models.TextField(blank=True, null=True, verbose_name='Описание')


class GenreTitle(models.Model):
    genre = models.ForeignKey(
        Genre,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    title = models.ForeignKey(
        Title,
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )


    class Meta:
        constraints = [
            UniqueConstraint(fields=['genre', 'title'], name='genre_and_title')
        ]
