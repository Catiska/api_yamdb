from rest_framework import viewsets
from rest_framework import filters


from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from .serializers import (
    ReviewSerializer, CommentSerializer, CategorySerializer,
    GenreSerializer, TitleSerializer,
    TitleCreateOrUpdateSerializer, UserSerializer
)
from .permissions import (
    IsAdminOrSuperuserOrReadOnly,
    IsAdminModerAuthorOrReadonly
)
from .mixins import ListCreateDeleteViewSet
from reviews.models import Category, Genre, Title, GenreTitle, Review, Comment, User


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели User.
    Получение юзера или создание нового.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = (filters.SearchFilter,)
    lookup_field = 'username'
    lookup_value_regex = "[\w.@+-]+"
    permission_classes = (IsAdminOrSuperuserOrReadOnly,)
    search_fields = ('username',)


# class MeUserViewSet(ListCreateDeleteViewSet):
#     """
#     Вьюсет для просмотра и редактирования своег опрофиля.
#     """
    


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModerAuthorOrReadonly,)

    def get_queryset(self):
        return get_object_or_404(
            Review, id=self.kwargs.get('title_id')
        ).reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Review, id=self.kwargs.get('title_id'))
        serializer.save(
            author=self.request.user,
            title=title
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = (IsAdminModerAuthorOrReadonly,)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()


    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)





class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrSuperuserOrReadOnly,)
    lookup_field = 'slug'
    lookup_value_regex = "[-a-zA-Z0-9_]+"
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)



class GenreViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrSuperuserOrReadOnly,)
    lookup_field = 'slug'
    lookup_value_regex = "[-a-zA-Z0-9_]+"
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


# Необходимо добавлять rating.
class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrSuperuserOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        'category__slug',
        'genre__slug',
        'name',
        'year',
    )

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return TitleCreateOrUpdateSerializer
        return TitleSerializer
