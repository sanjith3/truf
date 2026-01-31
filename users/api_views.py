from rest_framework import status, views
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from core.utils import get_sms_provider
from .serializers import LoginRequestSerializer, VerifyOTPRequestSerializer, UserSerializer

User = get_user_model()

class LoginAPIView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginRequestSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone_number']
            user, created = User.objects.get_or_create(phone_number=phone)
            otp = user.generate_demo_otp()
            
            # Use Service Layer
            sms = get_sms_provider()
            sms.send_otp(phone, otp)
            
            response_data = {"message": "OTP sent successfully"}
            from django.conf import settings
            if settings.DEBUG:
                response_data["debug_otp"] = otp
                
            return Response(response_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPAPIView(views.APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPRequestSerializer(data=request.data)
        if serializer.is_valid():
            phone = serializer.validated_data['phone_number']
            otp_input = serializer.validated_data['otp']
            
            try:
                user = User.objects.get(phone_number=phone)
                if user.otp == otp_input:
                    user.otp = None
                    user.save()
                    
                    refresh = RefreshToken.for_user(user)
                    return Response({
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                        'user': UserSerializer(user).data
                    })
                return Response({"error": "Invalid OTP"}, status=status.HTTP_400_BAD_REQUEST)
            except User.DoesNotExist:
                return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
