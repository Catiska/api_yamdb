from datetime import datetime as dt

import re

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django.core.validators import EmailValidator, RegexValidator
from django.db.models import Avg
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404


from reviews.models import (
    Category, Genre, Title, GenreTitle, Review, Comment, User)

class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для пользователей."""

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'role', 'bio',
                  'email')
        
    def validate_username(self, data):
        if data == 'me':
            raise ValidationError(
                'Имя "me" зарезервировано, используйте другое'
            )
        if not re.search(r'^[\w.@+-]+\Z', data):
            raise ValidationError('В имени пользователя использованы недопустимые символы')
        return data



class GuestSerializer(UserSerializer):
    """Сериализатор для получения данных своей учетной записи."""
    role = serializers.CharField(read_only=True)

    # class Meta:
    #     model = User
    #     fields = ('username', 'first_name', 'last_name', 'role', 'bio',
    #               'email')


class GetTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True)
    confirmation_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True)#, validators=[UniqueValidator(queryset=User.objects.all())])
    email = serializers.EmailField(max_length=254, required=True)#, validators=[UniqueValidator(queryset=User.objects.all())])

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, data):
        if data == 'me':
            raise ValidationError(
                'Имя "me" зарезервировано, используйте другое'
            )
        if not re.search(r'^[\w.@+-]+\Z', data):
            raise ValidationError('В имени пользователя использованы недопустимые символы')
        return data
    
    def validate(self, data):
        username_check = User.objects.filter(username=data.get('username'))
        email_check = User.objects.filter(email=data.get('email'))
        if email_check and not username_check:
            raise ValidationError("Другой пользователь с такой почтой уже существует")
        if not email_check and username_check:
            raise ValidationError("Вы ввели неверную почту")
        return data


class MeSerializer(UserSerializer):
    """
    Сериализатор для профиля Users,
    наследованный от модели UserSerializer.
    """
    role = serializers.CharField(read_only=True)



class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели отзывов."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault(),
        read_only=True
    )

    class Meta:
        model = Review
        fields = '__all__'
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
        fields = '__all__'
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
    rating = serializers.IntegerField(read_only=True)
    category = CategorySerializer(read_only=True, many=False)

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'genre', 'category', 'description',
                  'rating')


class TitleCreateOrUpdateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(many=True,
                                         slug_field='slug',
                                         queryset=Genre.objects.all())
    rating = serializers.SerializerMethodField('get_rating')
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
        if value > dt.now().year or value < 0:
            raise serializers.ValidationError('Год выхода не может превышать текущий год или быть отрицательным!')
        return value
    

    def validate_genre(self, value):
        if not value:
            raise serializers.ValidationError('Нельзя передавать пустой список жанров!')
        return value

    def get_rating(self, obj):
        reviews = Review.objects.filter(title=obj)
        if len(reviews) == 0:
            return None
        rating = reviews.aggregate(Avg('score'))
        return rating['score__avg']
