from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import Turf
from .serializers import TurfListSerializer, TurfDetailSerializer
from core.services.location import LocationService

class TurfViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows turfs to be viewed.
    Supports:
    - Nearby filtering (?lat=x&long=y&radius=5)
    - Standard filtering (?city=x&sports__name=y&min_price=0&max_price=1000)
    """
    queryset = Turf.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['city', 'sports__name']
    search_fields = ['name', 'address', 'city']
    ordering_fields = ['price_per_hour', 'created_at', 'distance']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Get location params
        lat = self.request.query_params.get('lat')
        lon = self.request.query_params.get('long')
        radius = float(self.request.query_params.get('radius', 5)) # Default 5km

        # Standard filters
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price_per_hour__gte=min_price)
        if max_price:
            queryset = queryset.filter(price_per_hour__lte=max_price)

        if lat and lon:
            try:
                queryset = LocationService.get_nearby_turfs(
                    queryset, float(lat), float(lon), radius
                )
            except (ValueError, TypeError):
                pass
                
        return queryset

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TurfDetailSerializer
        return TurfListSerializer
