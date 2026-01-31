from rest_framework import views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from turfs.models import Turf, SportType

class AppConfigAPIView(views.APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        cities = Turf.objects.filter(is_active=True).values_list('city', flat=True).distinct()
        sports = SportType.objects.all().values('id', 'name', 'icon')
        
        return Response({
            "cities": list(cities),
            "sports": list(sports),
            "amenities_options": ["Floodlights", "Water", "Parking", "Changing Room", "Locker"],
            "price_range": {
                "min": 500,
                "max": 5000
            }
        })
