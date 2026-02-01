from django.urls import path
from . import views

app_name = 'turfs'

urlpatterns = [
    path('', views.turf_list, name='list'),
    path('<int:turf_id>/', views.turf_detail, name='detail'),
    path('add/', views.add_turf, name='add'),
    path('<int:turf_id>/edit/', views.edit_turf, name='edit'),
    path('<int:turf_id>/images/', views.manage_turf_images, name='manage_images'),
    path('<int:turf_id>/operations/', views.turf_operations, name='operations'),
    path('<int:turf_id>/toggle-status/', views.toggle_today_status, name='toggle_status'),
    path('<int:turf_id>/emergency-block/', views.toggle_emergency_block, name='toggle_emergency'),
]
