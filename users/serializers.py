from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'is_turf_owner', 'is_owner_approved']

class LoginRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

class VerifyOTPRequestSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    otp = serializers.CharField(max_length=6)
