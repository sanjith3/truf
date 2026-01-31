from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from users.models import CustomUser
from turfs.models import Turf

@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard with KPIs"""
    from bookings.models import Booking
    from payments.models import DemoPayment
    from django.db.models import Sum, Count
    import datetime
    
    today = datetime.date.today()
    
    # KPIs
    total_users = CustomUser.objects.count()
    total_turfs = Turf.objects.filter(is_active=True).count()
    pending_approvals = CustomUser.objects.filter(
        is_turf_owner=True,
        is_owner_approved=False
    ).count()
    today_bookings = Booking.objects.filter(booking_date=today).count()
    
    revenue_data = DemoPayment.objects.filter(status='SUCCESS').aggregate(Sum('amount'))
    total_revenue = revenue_data['amount__sum'] or 0
    
    # Recent activity
    recent_turfs = Turf.objects.select_related('owner').order_by('-created_at')[:5]
    recent_bookings = Booking.objects.select_related('turf', 'user').order_by('-created_at')[:5]
    
    context = {
        'pending_count': pending_approvals,
        'kpi_data': {
            'total_users': total_users,
            'total_turfs': total_turfs,
            'pending_approvals': pending_approvals,
            'today_bookings': today_bookings,
            'total_revenue': total_revenue,
        },
        'recent_turfs': recent_turfs,
        'recent_bookings': recent_bookings,
    }
    return render(request, 'admin/dashboard.html', context)

@staff_member_required
def venue_directory(request):
    """List all approved turfs with filters and pagination"""
    # Get filter parameters
    search = request.GET.get('search', '')
    city_filter = request.GET.get('city', '')
    status_filter = request.GET.get('status', '')
    sort_by = request.GET.get('sort', '-created_at')
    
    # Base queryset
    turfs = Turf.objects.select_related('owner', 'owner__owner_profile').prefetch_related('sports')
    
    # Apply filters
    if search:
        turfs = turfs.filter(
            Q(name__icontains=search) | 
            Q(owner__phone_number__icontains=search) |
            Q(city__icontains=search)
        )
    
    if city_filter:
        turfs = turfs.filter(city=city_filter)
    
    if status_filter == 'active':
        turfs = turfs.filter(is_active=True)
    elif status_filter == 'inactive':
        turfs = turfs.filter(is_active=False)
    
    # Apply sorting
    turfs = turfs.order_by(sort_by)
    
    # Get unique cities for filter dropdown
    cities = Turf.objects.values_list('city', flat=True).distinct().order_by('city')
    
    # Pagination
    paginator = Paginator(turfs, 20)  # 20 turfs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Count pending approvals for sidebar
    pending_count = CustomUser.objects.filter(
        is_turf_owner=True,
        is_owner_approved=False
    ).count()
    
    context = {
        'page_obj': page_obj,
        'cities': cities,
        'search': search,
        'city_filter': city_filter,
        'status_filter': status_filter,
        'sort_by': sort_by,
        'pending_count': pending_count,
    }
    return render(request, 'admin/venue_directory.html', context)

@staff_member_required
def venue_detail(request, turf_id):
    """Detailed view of a specific turf"""
    turf = get_object_or_404(
        Turf.objects.select_related('owner', 'owner__owner_profile').prefetch_related(
            'sports', 'images', 'videos'
        ),
        id=turf_id
    )
    
    pending_count = CustomUser.objects.filter(
        is_turf_owner=True,
        is_owner_approved=False
    ).count()
    
    context = {
        'turf': turf,
        'pending_count': pending_count,
    }
    return render(request, 'admin/venue_detail.html', context)

@staff_member_required
def toggle_turf_status(request, turf_id):
    """Enable/Disable a turf"""
    if request.method == 'POST':
        turf = get_object_or_404(Turf, id=turf_id)
        turf.is_active = not turf.is_active
        turf.save()
        
        status = "activated" if turf.is_active else "deactivated"
        messages.success(request, f'Turf "{turf.name}" has been {status}.')
        
        return redirect('admin:venue_detail', turf_id=turf_id)
    
    return redirect('admin:venue_directory')

@staff_member_required
def turf_owners_list(request):
    """List all turf owners"""
    search = request.GET.get('search', '')
    status_filter = request.GET.get('status', '')
    
    owners = CustomUser.objects.filter(is_turf_owner=True).select_related('owner_profile').prefetch_related('turfs')
    
    if search:
        owners = owners.filter(
            Q(phone_number__icontains=search) |
            Q(owner_profile__business_name__icontains=search) |
            Q(owner_profile__contact_email__icontains=search)
        )
    
    if status_filter == 'approved':
        owners = owners.filter(is_owner_approved=True)
    elif status_filter == 'pending':
        owners = owners.filter(is_owner_approved=False)
    
    owners = owners.order_by('-owner_application_date')
    
    paginator = Paginator(owners, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    pending_count = CustomUser.objects.filter(
        is_turf_owner=True,
        is_owner_approved=False
    ).count()
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'pending_count': pending_count,
    }
    return render(request, 'admin/turf_owners_list.html', context)

@staff_member_required
def pending_approvals_list(request):
    """View to list all pending turf owner applications"""
    pending_owners = CustomUser.objects.filter(
        is_turf_owner=True,
        is_owner_approved=False
    ).select_related('owner_profile').prefetch_related('turfs').order_by('-owner_application_date')
    
    pending_count = pending_owners.count()
    
    context = {
        'pending_owners': pending_owners,
        'pending_count': pending_count,
        'title': 'Pending Turf Owner Approvals'
    }
    return render(request, 'admin/pending_approvals_list.html', context)

@staff_member_required
def pending_approval_detail(request, user_id):
    """View to show detailed information about a specific pending application"""
    owner = get_object_or_404(
        CustomUser.objects.select_related('owner_profile').prefetch_related(
            'turfs', 'turfs__images', 'turfs__sports', 'turfs__videos'
        ),
        id=user_id,
        is_turf_owner=True,
        is_owner_approved=False
    )
    
    pending_count = CustomUser.objects.filter(
        is_turf_owner=True,
        is_owner_approved=False
    ).count()
    
    context = {
        'owner': owner,
        'turf': owner.turfs.first(),
        'pending_count': pending_count,
        'title': f'Review Application - {owner.owner_profile.business_name}'
    }
    return render(request, 'admin/pending_approval_detail.html', context)

@staff_member_required
def approve_owner(request, user_id):
    """Approve a turf owner application"""
    if request.method == 'POST':
        owner = get_object_or_404(CustomUser, id=user_id, is_turf_owner=True)
        owner.is_owner_approved = True
        owner.save()
        
        # Activate all their turfs
        owner.turfs.all().update(is_active=True)
        
        messages.success(request, f'Successfully approved {owner.owner_profile.business_name}. Their turf is now live!')
        return redirect('admin:pending_approvals_list')
    
    return redirect('admin:pending_approvals_list')

@staff_member_required
def reject_owner(request, user_id):
    """Reject a turf owner application"""
    if request.method == 'POST':
        owner = get_object_or_404(CustomUser, id=user_id, is_turf_owner=True)
        business_name = owner.owner_profile.business_name
        owner.delete()
        
        messages.warning(request, f'Rejected application from {business_name}. All data has been removed.')
        return redirect('admin:pending_approvals_list')
    
    return redirect('admin:pending_approvals_list')
