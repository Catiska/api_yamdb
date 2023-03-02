from pprint import pprint
from django.urls import path, include

from rest_framework import routers

from api.views import CategoryViewSet, ReviewViewSet, CommentViewSet, GenreViewSet, TitleViewSet, UserViewSet

app_name = 'api'

router_v1 = routers.DefaultRouter()
router_v1.register('categories', CategoryViewSet)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router_v1.register('genres', GenreViewSet)
router_v1.register('titles', TitleViewSet)

router_v1.register('users', UserViewSet, basename='users')

urlpatterns = [
    path('v1/', include(router_v1.urls))
]

pprint(router_v1.urls)
