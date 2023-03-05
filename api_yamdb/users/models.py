from django.db import models
from django.contrib.auth.models import AbstractUser

from .roles import UserRole
from api.validators import validate_username


class User(AbstractUser):
    """Модель пользователя."""
    username = models.CharField( 
        max_length=150,
        unique=True,
        blank=False,
        null=False,
        validators=[validate_username]
    )
    role = models.CharField(
        'Роль',
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.USER
    )
    bio = models.TextField(
        'Биография',
        blank=True
    )
    email = models.EmailField(
        'Email',
        max_length=254,
        unique=True,  # этого нет в базовой модели
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
        return self.role == UserRole.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == UserRole.MODERATOR

    @property
    def is_user(self):
        return self.role == UserRole.USER
