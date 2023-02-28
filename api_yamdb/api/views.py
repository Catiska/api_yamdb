from rest_framework import viewsets

from rest_framework.decorators import action

from rest_framework.response import Response

from rest_framework.pagination import PageNumberPagination

from rest_framework import filters

from reviews.models import Category, Genre, Title, GenreTitle, User

from api.serializers import CategorySerializer


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    lookup_field = 'slug'
    lookup_value_regex = "[-a-zA-Z0-9_]+"
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
