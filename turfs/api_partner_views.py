from rest_framework import views, status, response, permissions
from .api_partner_serializer import PartnerRegistrationSerializer
from .serializers import TurfDetailSerializer

class PartnerRegistrationView(views.APIView):
    """
    API endpoint for Turf Owners to register their venue.
    Endpoint: /api/v1/partner/register/
    Method: POST (multipart/form-data)
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, format=None):
        serializer = PartnerRegistrationSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            turf = serializer.save()
            # Return full detail of created turf
            return response.Response({
                "message": "Turf registered successfully! It is pending approval.",
                "data": TurfDetailSerializer(turf, context={'request': request}).data
            }, status=status.HTTP_201_CREATED)
        
        return response.Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
