from django.contrib import admin
from .models import Booking
from core.admin_site import admin_site

class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'user', 'turf', 'booking_date', 'start_time', 'status', 'payment_status')
    list_filter = ('status', 'payment_status', 'booking_date')
    search_fields = ('booking_id', 'user__phone_number', 'turf__name')

admin_site.register(Booking, BookingAdmin)
