from django.core.exceptions import ValidationError
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import (Category, Comment, Genre, GenreTitle, Review,
                            Title)
from users.models import User
from .validators import validate_genre


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'role', 'bio',
                  'email')


class GuestSerializer(UserSerializer):
    """Сериализатор для получения данных своей учетной записи."""
    role = serializers.CharField(read_only=True)


class GetTokenSerializer(serializers.ModelSerializer):
    """Сериализатор получения токена."""
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class SignupSerializer(serializers.ModelSerializer):
    """Сериализатор регистрации пользователя."""
    username = serializers.CharField(max_length=150,
                                     required=True)
    email = serializers.EmailField(max_length=254,
                                   required=True)

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate(self, data):
        """Проверка корректности email и запрет на повторную регистрацию."""
        username_check = User.objects.filter(
            username=data.get('username')).exists()
        email_check = User.objects.filter(
            email=data.get('email')).exists()
        if email_check and not username_check:
            raise ValidationError(
                "Другой пользователь с такой почтой уже существует")
        if not email_check and username_check:
            raise ValidationError("Вы ввели неверную почту")
        return data


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор модели категорий."""

    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор модели жанров."""

    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра модели произведений."""
    genre = GenreSerializer(many=True)
    rating = serializers.SerializerMethodField('get_rating')
    category = CategorySerializer(read_only=True, many=False)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'genre', 'category', 'description',
                  'rating')

    def get_rating(self, obj):
        obj = obj.reviews.all().aggregate(rating=Avg('score'))
        return obj['rating']


class TitleCreateOrUpdateSerializer(serializers.ModelSerializer):
    """Сериализатор создания или редактирования модели произведений."""
    genre = serializers.SlugRelatedField(many=True,
                                         slug_field='slug',
                                         queryset=Genre.objects.all())
    rating = serializers.IntegerField(read_only=True)
    category = serializers.SlugRelatedField(slug_field='slug',
                                            queryset=Category.objects.all())

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'genre', 'category', 'description',
                  'rating')

    def create(self, validated_data):
        genres = validated_data.pop('genre')
        title = Title.objects.create(**validated_data)
        for current_genre in genres:
            GenreTitle.objects.create(
                genre=current_genre, title=title
            )
        return title

    def validate_genre(selv,value):
        return validate_genre(value)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели отзывов."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date', 'title')
        read_only_fields = ('author', 'title')

    def validate(self, data):
        """Проверка повторного отзыва к текущему произведению."""
        request = self.context['request']
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
                request.method == 'POST'
                and Review.objects.filter(title=title,
                                          author=request.user).exists()
        ):
            raise ValidationError(
                'Вы уже оставляли отзыв к этому произведению'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор модели комментариев к отзыву."""
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)
        read_only_fields = ('author', 'review')
