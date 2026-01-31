from django.contrib import admin
from django.db.models import Sum
# We will import models inside the method to avoid circular imports
import datetime

class TurfSpotAdminSite(admin.AdminSite):
    site_header = "TurfSpot Super Admin"
    site_title = "TurfSpot Admin"
    index_title = "Platform Management Dashboard"
    index_template = "admin/index.html"

    def index(self, request, extra_context=None):
        from users.models import CustomUser, TurfOwnerProfile
        from turfs.models import Turf
        from bookings.models import Booking
        from payments.models import DemoPayment
        
        # Gather KPI Data
        today = datetime.date.today()
        
        total_users = CustomUser.objects.count()
        total_turfs = Turf.objects.filter(is_active=True).count()
        today_bookings = Booking.objects.filter(booking_date=today).count()
        
        # Pending Approvals
        pending_owners = CustomUser.objects.filter(
            is_turf_owner=True,
            is_owner_approved=False
        ).select_related('owner_profile').prefetch_related('turfs', 'turfs__images', 'turfs__sports')
        
        # Simple revenue calculation
        revenue_data = DemoPayment.objects.filter(status='SUCCESS').aggregate(Sum('amount'))
        total_revenue = revenue_data['amount__sum'] or 0
        
        kpi_data = {
            'total_users': total_users,
            'total_turfs': total_turfs,
            'today_bookings': today_bookings,
            'total_revenue': total_revenue,
            'pending_approvals': pending_owners.count()
        }
        
        extra_context = extra_context or {}
        extra_context['kpi_data'] = kpi_data
        extra_context['pending_owners'] = pending_owners
        
        return super().index(request, extra_context)

admin_site = TurfSpotAdminSite(name='turf_admin')
