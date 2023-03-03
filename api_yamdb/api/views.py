from django.forms.models import model_to_dict
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from reviews.models import Category, Genre, Review, Title, User
from .mixins import ListCreateDeleteViewSet
from .permissions import (IsAdminModerAuthorOrReadonly, IsAdminOrSuperuser,
                          IsAdminOrSuperuserOrReadOnly)
from .serializers import (CategorySerializer, CommentSerializer,
                          GenreSerializer, GetTokenSerializer, GuestSerializer,
                          ReviewSerializer, SignupSerializer,
                          TitleCreateOrUpdateSerializer, TitleSerializer,
                          UserSerializer)
from .validators import validate_username


class UserViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrSuperuser,)
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


class GetTokenView(APIView):
    """Получам JWT-токен в ответ на отправку POST-запроса
    по адресу /api/v1/auth/token/ с данными username и confirmation_code."""
    permission_classes = (permissions.AllowAny,)

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
    по адресу /api/v1/auth/signup/ с данными username и email"""
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        email = serializer.data['email']
        username = validate_username(serializer.data['username'])
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
    permission_classes = (IsAdminOrSuperuserOrReadOnly,)
    lookup_field = 'slug'
    lookup_value_regex = "[-a-zA-Z0-9_]+"
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class GenreViewSet(ListCreateDeleteViewSet):
    """Миксины и вьюсет для модели жанров."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrSuperuserOrReadOnly,)
    lookup_field = 'slug'
    lookup_value_regex = "[-a-zA-Z0-9_]+"
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


class TitleViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели произведений."""
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

    def get_queryset(self):
        if self.request.query_params.get('genre'):
            objec = get_object_or_404(Genre,
                                      slug=self.request.query_params.get(
                                          'genre'))
            queryset = objec.title_set.all()
        elif self.request.query_params.get('category'):
            objec = get_object_or_404(Category,
                                      slug=self.request.query_params.get(
                                          'category'))
            queryset = objec.titles.all()
        else:
            queryset = Title.objects.all()
        return queryset


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели отзывов."""
    serializer_class = ReviewSerializer
    permission_classes = (IsAdminModerAuthorOrReadonly,)

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
    permission_classes = (IsAdminModerAuthorOrReadonly,)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
