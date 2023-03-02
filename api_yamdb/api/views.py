from rest_framework import viewsets
from rest_framework import filters
from rest_framework import mixins
from rest_framework import permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from api.serializers import ReviewSerializer, CommentSerializer
from api.serializers import CategorySerializer, GenreSerializer
from api.serializers import TitleSerializer, TitleCreateOrUpdateSerializer, UserSerializer

from reviews.models import Category, Genre, Title, GenreTitle, Review, Comment, User


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    queryset = User.objects.all()
    serializer_class = UserSerializer
    lookup_field = 'username'
    lookup_value_regex = "[\w.@+-]+"
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)

    @action(detail=True, url_path='users/me', methods=['get'], )
    def get_my_profile(self, request, number):

        def retrieve(self, request, *args, **kwargs):
            # instance = self.get_object()
            instance = get_object()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)
        
        def get_object():
            return User.objects.get(id=1)

        # def update(self, request, *args, **kwargs):
        #     partial = kwargs.pop('partial', False)
        #     instance = self.get_object()
        #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
        #     serializer.is_valid(raise_exception=True)
        #     self.perform_update(serializer)

        #     if getattr(instance, '_prefetched_objects_cache', None):
        #         # If 'prefetch_related' has been applied to a queryset, we need to
        #         # forcibly invalidate the prefetch cache on the instance.
        #         instance._prefetched_objects_cache = {}

        #     return Response(serializer.data)

        # def perform_update(self, serializer):
        #     serializer.save()

        # def partial_update(self, request, *args, **kwargs):
        #     kwargs['partial'] = True
        #     return self.update(request, *args, **kwargs)

        return retrieve(self, self.request)

        # posts = Post.objects.select_related('author', 'group').all().order_by('-pub_date')[:int(number)]
        # return detail(self, self.request, posts)


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    # permission_classes = (,)

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
    # permission_classes = (,)

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()


    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class ListCreateDeleteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                              mixins.ListModelMixin, viewsets.GenericViewSet):
    pass


class CategoryViewSet(ListCreateDeleteViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    lookup_value_regex = "[-a-zA-Z0-9_]+"
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)


# class UserViewSet(viewsets.ModelViewSet):
#     """
#     Вьюсет для модели User.
#     """
#     pass
    

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
