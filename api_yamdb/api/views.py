from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMessage
from rest_framework import viewsets, status, permissions
from rest_framework import filters
from rest_framework import mixins

from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .permissions import (IsAdminOrSuperuserOrReadOnly,
                          IsAdminModerAuthorOrReadonly)
from .serializers import (ReviewSerializer, CommentSerializer,
                          CategorySerializer, GenreSerializer,
                          TitleSerializer, TitleCreateOrUpdateSerializer,
                          UserSerializer, GetTokenSerializer, SignupSerializer)
from reviews.models import (Category, Genre, Title, GenreTitle, Review,
                            Comment, User)


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


class ListCreateDeleteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                              mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    lookup_value_regex = "[-a-zA-Z0-9_]+"
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class UserViewSet(viewsets.ModelViewSet):
    """
    Вьюсет для модели User.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    

class GenreViewSet(ListCreateDeleteViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    lookup_value_regex = "[-a-zA-Z0-9_]+"
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


# Необходимо добавлять rating.
class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
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


class GetTokenView(APIView):
    """Получам JWT-токен в ответ на отправку POST-запроса
    по адресу /api/v1/auth/token/ с данными usernamr и confirmation_code."""
    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data.get('username')
        user = get_object_or_404(User, username=username)
        confirmation_code = serializer.validated_data.get('confirmation_code')
        if confirmation_code != user.confirmation_code:
            return Response('Вы ввели неверный код подтверждения',
                            status=status.HTTP_400_BAD_REQUEST)
        token = str(RefreshToken.for_user(user).access_token)
        return Response(token, status=status.HTTP_200_OK)


class SignupView(APIView):
    """Чтобы получить код подтверждения на почту, надо отправить POST-запрос
    по адрему /api/v1/auth/signup/ с данными username и email"""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        email = serializer.validated_data.get['email']
        username = serializer.validated_data.get['username']
        user, _ = User.objects.get_or_create(email=email, username=username)
        confirmation_code = default_token_generator.make_token(user)
        confirmation_message = f'Ваш код подтвержения {confirmation_code}'
        user.email_user(subject='Код подтверждения',
                        message=confirmation_message)
        user.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
