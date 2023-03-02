from rest_framework import mixins
from rest_framework import viewsets


class ListCreateDeleteViewSet(mixins.CreateModelMixin, mixins.DestroyModelMixin,
                              mixins.ListModelMixin, viewsets.GenericViewSet):
    pass
