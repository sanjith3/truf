from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('book/<int:turf_id>/', views.book_slot, name='book'),
    path('payment/<uuid:booking_id>/', views.payment_view, name='payment'),
    path('success/<uuid:booking_id>/', views.booking_success, name='success'),
]
