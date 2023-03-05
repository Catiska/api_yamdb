from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from django.core.exceptions import ValidationError

from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly

from reviews.models import Category, Genre, Review, Title
from users.models import User
from .mixins import ListCreateDeleteViewSet
from .permissions import (IsAdminModerAuthorOrReadonly, IsAdminOrSuperuser,
                          IsAdminOrSuperuserOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer, GuestSerializer,
                          ReviewSerializer, SignupSerializer,
                          TitleCreateOrUpdateSerializer, TitleSerializer,
                          UserSerializer)
from .validators import validate_username
from .filters import TitleFilter


from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.tokens import default_token_generator


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsAdminOrSuperuser,)
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    http_method_names = ('get', 'post', 'delete', 'patch')

    @action(methods=('GET', 'PATCH'),
            detail=False,
            permission_classes=(permissions.IsAuthenticated,),
            url_path='me')
    def get_me_info(self, request):
        if request.method == 'PATCH' and (
                request.user.is_admin or request.user.is_superuser):
            serializer = UserSerializer(request.user,
                                        data=request.data,
                                        partial=True)
        elif request.method == 'PATCH':
            serializer = GuestSerializer(request.user,
                                         data=request.data,
                                         partial=True)
        else:
            serializer = GuestSerializer(request.user,
                                         data=model_to_dict(request.user), )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


@receiver(post_save, sender=User)
def post_save(sender, instance, created, **kwargs):
    if created:
        confirmation_code = default_token_generator.make_token(
            instance
        )
        instance.confirmation_code = confirmation_code
        instance.save()


class GetTokenView(APIView):
    """Получам JWT-токен в ответ на отправку POST-запроса
    по адресу /api/v1/auth/token/ с данными username и confirmation_code."""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
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
    по адресу /api/v1/auth/signup/ с данными username и email"""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data['email']
        try: 
            username = validate_username(serializer.data['username'])
        except ValidationError as error:
            return Response(error, status=status.HTTP_400_BAD_REQUEST)
        user, _ = User.objects.get_or_create(email=email, username=username)
        confirmation_code = user.confirmation_code
        confirmation_message = f'Ваш код подтверждения {confirmation_code}'

        user.email_user(subject='Код подтверждения',
                        message=confirmation_message)
        user.save()
        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(ListCreateDeleteViewSet):
    """Вьюсет для модели категорий."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrSuperuserOrReadOnly,)
    lookup_field = 'slug'
    lookup_value_regex = "[-a-zA-Z0-9_]+"
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(ListCreateDeleteViewSet):
    """Миксины и вьюсет для модели жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrSuperuserOrReadOnly,)
    lookup_field = 'slug'
    lookup_value_regex = "[-a-zA-Z0-9_]+"
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели произведений."""
    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrSuperuserOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return TitleCreateOrUpdateSerializer
        return TitleSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели отзывов."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminModerAuthorOrReadonly,)

    def get_queryset(self):
        return get_object_or_404(
            Title, id=self.kwargs.get('title_id')
        ).reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(
            author=self.request.user,
            title=title
        )


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели комментариев."""
    serializer_class = CommentSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminModerAuthorOrReadonly,)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
