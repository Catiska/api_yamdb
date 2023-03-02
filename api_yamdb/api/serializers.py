from datetime import datetime as dt

from django.core.validators import EmailValidator, RegexValidator
from django.db.models import Avg
from rest_framework import serializers
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from reviews.models import (Category, Genre, Title, GenreTitle, Review,
                            Comment, User)


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'role', 'bio',
                  'email')


class GuestSerializer(serializers.ModelSerializer):
    """Сериализатор для получения данных своей учетной записи."""
    role = serializers.CharField(read_only=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'role', 'bio',
                  'email')


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(max_length=254, required=True)

    class Meta:
        model = User
        fields = ('username', 'email')
        validators = [EmailValidator, RegexValidator(
            regex=r'^[\w.@+-]',
            message='В имени пользователя использованы недопустимые символы')]

    def validate_username(self, data):
        name = data.lower()
        if name == 'me':
            raise ValidationError(
                'Имя "me" зарезервировано, используйте другое'
            )
        return data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели отзывов."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'author', 'score', 'text', 'pub_date', 'title')
        read_only_fields = ('author', 'title')

    def validate_score(self, score):
        """Валидация введенной оценки."""
        if 10 < score < 0:
            raise ValidationError(
                'Оценка произведения должна быть в диапазоне от 1 до 10 баллов'
            )

    def validate(self, data):
        """Проверка повторного отзыва к текущему произведению."""
        request = self.context['request']
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
                request.method == 'POST' and
                Review.objects.filter(title=title,
                                      author=request.user).exists()
        ):
            raise ValidationError(
                'Вы уже оставляли отзыв к этому произведению'
            )
        return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор можели комментариев к отзыву."""

    class Meta:
        model = Comment
        fields = ('id', 'author', 'text', 'pub_date', 'review')
        read_only_fields = ('author', 'review')


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug',)


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug',)


class TitleSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True)
    rating = serializers.SerializerMethodField('get_rating')
    category = CategorySerializer(read_only=True, many=False)

    def get_rating(self, obj):
        reviews = Review.objects.filter(title=obj)
        if len(reviews) == 0:
            return None
        rating = reviews.aggregate(Avg('score'))
        return rating['score__avg']

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'genre', 'category', 'description',
                  'rating')


class TitleCreateOrUpdateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(many=True,
                                         slug_field='slug',
                                         queryset=Genre.objects.all())
    rating = serializers.IntegerField(read_only=True,
                                      default=10)
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

    def validate_year(self, value):
        if value > dt.now().year:
            raise serializers.ValidationError(
                'Год выхода не может превышать текущий год!'
            )
        return value
