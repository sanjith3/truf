from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home, name='home'),
    path('platform-admin/', views.platform_admin_dashboard, name='platform_admin'),
    path('platform-admin/investor-insights/', views.investor_dashboard, name='investor_insights'),
    path('platform-admin/users/', views.admin_user_list, name='admin_users'),
    path('platform-admin/revenue/', views.admin_revenue_list, name='admin_revenue'),
    path('platform-admin/turfs/', views.admin_turf_list, name='admin_turfs'),
    path('platform-admin/pending-owners/', views.admin_pending_owners, name='admin_pending_owners'),
    path('platform-admin/review-application/<int:user_id>/', views.review_owner_application, name='review_application'),
    path('platform-admin/approve-owner/<int:user_id>/', views.approve_owner, name='approve_owner'),
    path('platform-admin/reject-owner/<int:user_id>/', views.reject_owner, name='reject_owner'),
    path('platform-admin/approve-turf/<int:turf_id>/', views.approve_turf, name='approve_turf'),
    path('platform-admin/approve-ad/<int:ad_id>/', views.approve_ad, name='approve_ad'),
    path('platform-admin/turfs/<int:turf_id>/review/', views.admin_turf_review, name='admin_turf_review'),
    path('platform-admin/turfs/<int:turf_id>/hide/', views.hide_turf, name='hide_turf'),
    path('platform-admin/bookings/', views.admin_booking_list, name='admin_bookings'),
]
