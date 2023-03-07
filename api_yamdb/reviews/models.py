from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint

from users.models import User

from api_yamdb.settings import SYMBOLS_TO_SHOW

from api.validators import validate_year


class CategoryGenre(models.Model):
    """
    Абстрактная модель для таблиц:
    Жанры и Категории.
    """
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        abstract = True


class Category(CategoryGenre):

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'

    def __str__(self):
        return self.name


class Genre(CategoryGenre):

    class Meta:
        ordering = ('name',)
        verbose_name = 'Жанр'

    def __str__(self):
        return self.name


class Title(models.Model):
    """Модель произведения."""
    name = models.CharField(max_length=256,
                            verbose_name='Название произведения')
    year = models.IntegerField(
        verbose_name='Дата',
        validators=[validate_year, ]
    )
    genre = models.ManyToManyField(Genre, through='GenreTitle')
    category = models.ForeignKey(
        Category,
        null=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        verbose_name='Категория'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание')

    class Meta:
        ordering = ('name',)


class GenreTitle(models.Model):
    """Модель связи произведения и жанров."""
    genre = models.ForeignKey(
        Genre,
        null=True,
        on_delete=models.SET_NULL
    )
    title = models.ForeignKey(
        Title,
        null=True,
        on_delete=models.SET_NULL
    )

    class Meta:
        constraints = [
            UniqueConstraint(fields=['genre', 'title'], name='genre_and_title')
        ]


class Review(models.Model):
    """Модель отзыва на произведение."""
    text = models.CharField('Текст отзыва', max_length=500)
    score = models.PositiveSmallIntegerField(
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
        return self.text[:SYMBOLS_TO_SHOW]


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
        return self.text[:SYMBOLS_TO_SHOW]
