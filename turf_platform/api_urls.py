from django.urls import path, include
from rest_framework.routers import DefaultRouter
from turfs.api_views import TurfViewSet
from users.api_views import LoginAPIView, VerifyOTPAPIView

from core.api_views import AppConfigAPIView

from turfs.api_partner_views import PartnerRegistrationView

router = DefaultRouter()
router.register(r'turfs', TurfViewSet, basename='turfs')

urlpatterns = [
    path('auth/login/', LoginAPIView.as_view(), name='api_login'),
    path('auth/verify/', VerifyOTPAPIView.as_view(), name='api_verify'),
    path('config/', AppConfigAPIView.as_view(), name='api_config'),
    path('partner/register/', PartnerRegistrationView.as_view(), name='api_partner_register'),
    path('', include(router.urls)),
]
