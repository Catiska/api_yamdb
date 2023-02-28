from pprint import pprint
from django.urls import include, path
from rest_framework import routers
from api.views import CategoryViewSet

app_name = 'api'

router = routers.DefaultRouter()
router.register('v1/categories', CategoryViewSet)
# router.register('v1/groups', GroupViewSet)
# router.register(r'v1/posts/(?P<post_id>\d+)/comments',
#                 CommentViewSet, basename='comments')
# router.register('v1/follow', FollowViewSet, basename='follow')

urlpatterns = [
    path('', include(router.urls)),
]

pprint(router.urls)