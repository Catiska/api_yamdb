from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.constraints import UniqueConstraint


ROLE_CHOICES = (
    ('admin', 'Администратор'),
    ('moderator', 'Модератор'),
    ('user', 'Пользователь'),
)


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField(
        max_length=150,
        unique=True,
        blank=False,
        null=False,
    )

    first_name = models.CharField(
        'Имя',
        max_length=150,
        blank=True,
        null=True,
    )

    last_name = models.CharField(
        'Фамилия',
        max_length=150,
        blank=True,
        null=True,
    )

    role = models.CharField(
        'Роль',
        max_length=20,
        choices=ROLE_CHOICES,
        default='user'
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )
    email = models.EmailField(
        'Email',
        max_length=254,
        unique=True,
        blank=False,
        null=False
    )
    confirmation_code = models.CharField(
        'Код подтверждения',
        max_length=50,
        null=True
    )

    class Meta:
        ordering = ['-id']
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_constraint'
            ),
        ]

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == "admin" or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == "moderator"

    @property
    def is_user(self):
        return self.role == 'user'


class Category(models.Model):
    """Модель категорий для произведений."""
    name = models.CharField(max_length=256,
                            verbose_name='Название категории')
    slug = models.SlugField(unique=True,
                            max_length=50,
                            verbose_name='Слаг категории')

    class Meta:
        ordering = ('name',)


class Genre(models.Model):
    """Модель жанров."""
    name = models.CharField(max_length=256,
                            verbose_name='Название жанра')
    slug = models.SlugField(unique=True,
                            max_length=50,
                            verbose_name='Слаг жанра')

    class Meta:
        ordering = ('name',)


class Title(models.Model):
    """Модель произведения."""
    name = models.CharField(max_length=256,
                            verbose_name='Название произведения')
    year = models.IntegerField(verbose_name='Дата')
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
