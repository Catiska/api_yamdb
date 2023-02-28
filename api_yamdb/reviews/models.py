from django.db import models

from django.db.models.constraints import UniqueConstraint


class Category(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название категории')
    slug = models.SlugField(unique=True, max_length=50, verbose_name='Слаг категории')


class Genre(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название жанра')
    slug = models.SlugField(unique=True, max_length=50, verbose_name='Слаг жанра')


class Title(models.Model):
    #  rating
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
