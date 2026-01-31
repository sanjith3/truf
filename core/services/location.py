import math
from django.db.models import F
from django.db.models.functions import ACos, Cos, Radians, Sin

class LocationService:
    @staticmethod
    def calculate_distance_query(lat, lon):
        """
        Returns a Django QuerySet expression to calculate distance in KM 
        using the Haversine formula (optimized for SQLite/PostgreSQL).
        """
        # Haversine formula
        # distance = 6371 * acos(cos(radians(lat1)) * cos(radians(lat2)) * cos(radians(lon2) - radians(lon1)) + sin(radians(lat1)) * sin(radians(lat2)))
        
        return 6371 * ACos(
            Cos(Radians(lat)) * Cos(Radians(F('latitude'))) *
            Cos(Radians(F('longitude')) - Radians(lon)) +
            Sin(Radians(lat)) * Sin(Radians(F('latitude')))
        )

    @staticmethod
    def get_nearby_turfs(queryset, lat, lon, radius_km=5):
        """
        Filters a queryset for turfs within a certain radius and adds a 'distance' field.
        """
        distance_expr = LocationService.calculate_distance_query(lat, lon)
        return queryset.annotate(distance=distance_expr).filter(distance__lte=radius_km).order_by('distance')
