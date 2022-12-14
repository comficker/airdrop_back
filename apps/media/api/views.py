from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from apps.base import pagination
from . import serializers
from apps.media import models


class MediaViewSet(viewsets.ModelViewSet):
    models = models.Media
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.MediaSerializer
    permission_classes = permissions.IsAuthenticatedOrReadOnly,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['title', 'description']
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        pass

    def destroy(self, request, *args, **kwargs):
        pass
