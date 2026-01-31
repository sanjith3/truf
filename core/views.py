from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count
from django.utils import timezone
from users.models import CustomUser
from turfs.models import Turf
from bookings.models import Booking
from payments.models import DemoPayment
import datetime

def home(request):
    return render(request, 'core/home.html')

@user_passes_test(lambda u: u.is_staff)
def platform_admin_dashboard(request):
    # KPIs
    total_users = CustomUser.objects.count()
    total_owners = CustomUser.objects.filter(is_turf_owner=True).count()
    pending_owners = CustomUser.objects.filter(is_turf_owner=True, is_owner_approved=False).count()
    active_turfs = Turf.objects.filter(is_active=True).count()
    pending_turfs_count = Turf.objects.filter(is_active=False).count()
    pending_turfs = Turf.objects.filter(is_active=False).select_related('owner')
    
    # Revenue
    revenue_data = DemoPayment.objects.filter(status='SUCCESS').aggregate(Sum('amount'))
    total_revenue = revenue_data['amount__sum'] or 0
    
    # Recent Bookings
    recent_bookings = Booking.objects.select_related('user', 'turf').order_by('-created_at')[:10]
    
    # Recent Owner Applications
    recent_owners = CustomUser.objects.filter(is_turf_owner=True).order_by('-owner_application_date')[:5]
    
    # Chart Data (Last 7 days bookings)
    today = timezone.now().date()
    dates = [(today - datetime.timedelta(days=i)) for i in range(6, -1, -1)]
    booking_counts = []
    for d in dates:
        count = Booking.objects.filter(booking_date=d).count()
        booking_counts.append(count)
    
    context = {
        'total_users': total_users,
        'total_owners': total_owners,
        'pending_owners': pending_owners,
        'active_turfs': active_turfs,
        'pending_turfs_count': pending_turfs_count,
        'pending_turfs': pending_turfs,
        'total_revenue': total_revenue,
        'recent_bookings': recent_bookings,
        'recent_owners': recent_owners,
        'chart_dates': [d.strftime('%a') for d in dates],
        'chart_data': booking_counts,
    }
    
    return render(request, 'admin/custom_dashboard.html', context)

@user_passes_test(lambda u: u.is_staff)
def admin_user_list(request):
    users = CustomUser.objects.all().order_by('-date_joined')
    return render(request, 'admin/reports/user_list.html', {'report_users': users, 'title': 'Platform Users'})

@user_passes_test(lambda u: u.is_staff)
def admin_revenue_list(request):
    payments = DemoPayment.objects.filter(status='SUCCESS').select_related('booking__user', 'booking__turf').order_by('-created_at')
    return render(request, 'admin/reports/revenue_list.html', {'payments': payments, 'title': 'Revenue History'})

@user_passes_test(lambda u: u.is_staff)
def admin_turf_list(request):
    turfs = Turf.objects.all().select_related('owner').order_by('-created_at')
    return render(request, 'admin/reports/turf_list.html', {'report_turfs': turfs, 'title': 'Venue Directory'})

@user_passes_test(lambda u: u.is_staff)
def admin_pending_owners(request):
    owners = CustomUser.objects.filter(is_turf_owner=True, is_owner_approved=False).order_by('-owner_application_date')
    return render(request, 'admin/reports/pending_owners.html', {'owners': owners, 'title': 'Pending Approvals'})

@user_passes_test(lambda u: u.is_staff)
def approve_owner(request, user_id):
    user = CustomUser.objects.get(id=user_id)
    user.is_owner_approved = True
    user.save()
    return redirect('core:platform_admin')

@user_passes_test(lambda u: u.is_staff)
def approve_turf(request, turf_id):
    turf = Turf.objects.get(id=turf_id)
    turf.is_active = True
    turf.save()
    return redirect('core:platform_admin')
