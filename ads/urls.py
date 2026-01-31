from django.urls import path
from . import views

app_name = 'ads'

urlpatterns = [
    path('click/<int:ad_id>/', views.ad_redirect, name='redirect'),
    path('dashboard/', views.advertiser_dashboard, name='dashboard'),
    path('create/', views.campaign_create, name='create'),
    path('<int:campaign_id>/', views.campaign_detail, name='detail'),
]
