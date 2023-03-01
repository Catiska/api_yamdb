from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from reviews.models import Review, Comment, Title


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор модели отзывов."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        default=serializers.CurrentUserDefault()
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

