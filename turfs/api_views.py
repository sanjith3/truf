from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Turf
from .serializers import TurfListSerializer, TurfDetailSerializer

class TurfViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows turfs to be viewed.
    Supports filtering by city and sports.
    """
    queryset = Turf.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'sports__name']
    search_fields = ['name', 'address', 'city']
    ordering_fields = ['price_per_hour', 'created_at']

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TurfDetailSerializer
        return TurfListSerializer
