from django.shortcuts import render, redirect, get_object_or_404
from django.db import models
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Sum, Count
from django.utils import timezone
from django.contrib import messages
from users.models import CustomUser
from turfs.models import Turf, TurfActivityLog
from bookings.models import Booking
from payments.models import DemoPayment
import datetime
from decimal import Decimal

def home(request):
    from ads.services import AdService
    # Fetch banner ad for HOME placement
    banners = AdService.get_served_ads('HOME', limit=1)
    banner_ad = banners[0] if banners else None
    
    # Record impression if ad exists
    if banner_ad:
        AdService.record_impression(banner_ad, user=request.user if request.user.is_authenticated else None)

    return render(request, 'core/home.html', {'banner_ad': banner_ad})

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
    revenue_data = Booking.objects.filter(payment_status='SUCCESS').aggregate(
        total_gross=Sum('total_amount'),
        total_commission=Sum('platform_commission'),
        total_convenience=Sum('convenience_fee'),
        total_payouts=Sum('owner_earnings')
    )
    total_revenue = revenue_data['total_gross'] or 0
    platform_commission_only = revenue_data['total_commission'] or 0
    total_convenience_fees = revenue_data['total_convenience'] or 0
    
    # Platform Earnings = 10% Commission + 100% Convenience Fee
    platform_earnings = platform_commission_only + total_convenience_fees
    owner_payouts = revenue_data['total_payouts'] or 0
    
    # Ad Revenue
    from ads.models import AdCampaign
    ad_stats = AdCampaign.objects.aggregate(
        total_ad_rev=Sum('spent_amount'),
        active_ads=Count('id', filter=models.Q(status='ACTIVE')),
        pending_ads_count=Count('id', filter=models.Q(status='PENDING_APPROVAL'))
    )
    total_ad_revenue = ad_stats['total_ad_rev'] or Decimal('0.00')
    active_ad_campaigns = ad_stats['active_ads'] or 0
    pending_ads_count = ad_stats['pending_ads_count'] or 0
    pending_ads = AdCampaign.objects.filter(status='PENDING_APPROVAL').select_related('advertiser')
    
    # Subscription Metrics
    from subscriptions.models import OwnerSubscription
    sub_stats = OwnerSubscription.objects.filter(status='ACTIVE', end_date__gt=timezone.now()).aggregate(
        mrr=Sum('plan__price'),
        active_subs=Count('id')
    )
    mrr = sub_stats['mrr'] or 0
    active_subscribers = sub_stats['active_subs'] or 0
    
    # Event Revenue (Tournaments)
    from events.services import EventService
    event_stats = EventService.get_platform_event_revenue()
    total_event_revenue = event_stats['total_event_revenue']
    
    # Recent Bookings (Only show paid bookings in the transactions list)
    recent_bookings = Booking.objects.filter(payment_status='SUCCESS').select_related('user', 'turf').order_by('-created_at')[:10]
    
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
        'platform_earnings': platform_earnings,
        'total_convenience_fees': total_convenience_fees,
        'owner_payouts': owner_payouts,
        'total_ad_revenue': total_ad_revenue,
        'active_ad_campaigns': active_ad_campaigns,
        'pending_ads_count': pending_ads_count,
        'pending_ads': pending_ads,
        'mrr': mrr,
        'active_subscribers': active_subscribers,
        'total_event_revenue': total_event_revenue,
        'recent_bookings': recent_bookings,
        'recent_owners': recent_owners,
        'chart_dates': [d.strftime('%a') for d in dates],
        'chart_data': booking_counts,
    }
    
    return render(request, 'admin/custom_dashboard.html', context)

@user_passes_test(lambda u: u.is_staff)
def investor_dashboard(request):
    """
    High-fidelity dashboard for investors and stakeholders.
    Focuses on MoM growth, revenue stream diversification, and health metrics.
    """
    from django.db.models.functions import TruncMonth
    from decimal import Decimal
    
    # 1. Current Month Revenue Breakdown
    now = timezone.now()
    first_of_this_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_of_last_month = (first_of_this_month - datetime.timedelta(days=1)).replace(day=1)

    def get_month_earnings(start_date, end_date):
        # Transactional Earnings
        bookings = Booking.objects.filter(payment_status='SUCCESS', created_at__range=(start_date, end_date)).aggregate(
            commission=Sum('platform_commission'),
            fees=Sum('convenience_fee')
        )
        comm = bookings['commission'] or Decimal('0.00')
        fees = bookings['fees'] or Decimal('0.00')
        
        # Subscription Earnings (Estimate based on active subs during period)
        # For simplicity in this demo, we'll take a snapshot of active MRR
        from subscriptions.models import OwnerSubscription
        sub_rev = OwnerSubscription.objects.filter(status='ACTIVE', created_at__lte=end_date).aggregate(Sum('plan__price'))['plan__price__sum'] or Decimal('0.00')
        
        # Ad Revenue (Current month spend)
        from ads.models import AdCampaign
        ad_rev = AdCampaign.objects.filter(created_at__range=(start_date, end_date)).aggregate(Sum('spent_amount'))['spent_amount__sum'] or Decimal('0.00')
        
        # Event Revenue (Commissions + Listing)
        from events.models import TournamentRegistration, Tournament
        event_listing = Tournament.objects.filter(is_paid_listing=True, created_at__range=(start_date, end_date)).aggregate(Sum('listing_fee'))['listing_fee__sum'] or Decimal('0.00')
        event_reg = TournamentRegistration.objects.filter(payment_status='SUCCESS', registered_at__range=(start_date, end_date)).aggregate(Sum('platform_commission'))['platform_commission__sum'] or Decimal('0.00')
        
        total = comm + fees + sub_rev + ad_rev + event_listing + event_reg
        return {
            'total': total,
            'commission': comm,
            'fees': fees,
            'subscriptions': sub_rev,
            'ads': ad_rev,
            'events': event_listing + event_reg
        }

    this_month = get_month_earnings(first_of_this_month, now)
    last_month = get_month_earnings(first_of_last_month, first_of_this_month)
    
    # Calculate MoM Growth
    growth_pct = 0
    if last_month['total'] > 0:
        growth_pct = ((this_month['total'] - last_month['total']) / last_month['total']) * 100
    
    # Growth History (Last 6 Months)
    history_raw = Booking.objects.filter(payment_status='SUCCESS').annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        rev=Sum('platform_commission') + Sum('convenience_fee')
    ).order_by('month')
    
    history_labels = [h['month'].strftime('%b %Y') for h in history_raw]
    history_values = [float(h['rev']) for h in history_raw]

    context = {
        'this_month': this_month,
        'last_month': last_month,
        'growth_pct': growth_pct,
        'history_labels': history_labels,
        'history_values': history_values,
        'top_source': max(this_month, key=lambda k: this_month[k] if k != 'total' else 0),
        'investor_ready': True # Flag for UI branding
    }
    
    return render(request, 'admin/investor_dashboard.html', context)

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
    owners = CustomUser.objects.filter(
        is_turf_owner=True, 
        is_owner_approved=False
    ).select_related('owner_profile').prefetch_related('turfs').order_by('-owner_application_date')
    return render(request, 'admin/reports/pending_owners.html', {'owners': owners, 'title': 'Pending Approvals'})

@user_passes_test(lambda u: u.is_staff)
def review_owner_application(request, user_id):
    """Detailed view of turf owner application for review"""
    owner = get_object_or_404(
        CustomUser.objects.select_related('owner_profile').prefetch_related(
            'turfs', 'turfs__images', 'turfs__sports', 'turfs__videos'
        ),
        id=user_id,
        is_turf_owner=True,
        is_owner_approved=False
    )
    
    formatted_date = owner.owner_application_date.strftime("%b %d, %Y") if owner.owner_application_date else "N/A"
    
    context = {
        'owner': owner,
        'turf': owner.turfs.first(),
        'title': f'Review Application - {owner.owner_profile.business_name}',
        'formatted_date': formatted_date,
    }
    return render(request, 'admin/reports/review_application.html', context)

@user_passes_test(lambda u: u.is_staff)
def approve_owner(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)
        user.is_owner_approved = True
        user.save()
        
        # Activate all their turfs
        user.turfs.all().update(is_active=True)
        
        messages.success(request, f'Successfully approved {user.owner_profile.business_name}. Their turf is now live!')
        return redirect('core:admin_pending_owners')
    
    return redirect('core:admin_pending_owners')

@user_passes_test(lambda u: u.is_staff)
def reject_owner(request, user_id):
    if request.method == 'POST':
        user = get_object_or_404(CustomUser, id=user_id)
        business_name = user.owner_profile.business_name
        user.delete()
        
        messages.warning(request, f'Rejected application from {business_name}. All data has been removed.')
        return redirect('core:admin_pending_owners')
    
    return redirect('core:admin_pending_owners')

@user_passes_test(lambda u: u.is_staff)
def approve_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    turf.is_active = True
    turf.save()
    messages.success(request, f'Turf {turf.name} is now ACTIVE.')
    
    # Redirect back to where we came from if it was a POST (Review page)
    if request.method == 'POST':
        return redirect('core:admin_turf_review', turf_id=turf.id)
    return redirect('core:platform_admin')

@user_passes_test(lambda u: u.is_staff)
def approve_ad(request, ad_id):
    from ads.models import AdCampaign
    ad = get_object_or_404(AdCampaign, id=ad_id)
    ad.status = 'ACTIVE'
    ad.save()
    messages.success(request, f'Ad Campaign "{ad.title}" is now ACTIVE.')
    return redirect('core:platform_admin')

@user_passes_test(lambda u: u.is_staff)
def hide_turf(request, turf_id):
    if request.method == 'POST':
        turf = get_object_or_404(Turf, id=turf_id)
        turf.is_active = False
        turf.save()
        messages.success(request, f'Successfully hidden {turf.name} from the app.')
        return redirect('core:admin_turf_review', turf_id=turf.id)
    return redirect('core:admin_turf_review', turf_id=turf_id)

@user_passes_test(lambda u: u.is_staff)
def admin_booking_list(request):
    bookings = Booking.objects.all().select_related('user', 'turf').order_by('-booking_date', '-time_slot')
    for b in bookings:
        b.short_id = str(b.booking_id)[:8] + '...'
    return render(request, 'admin/reports/booking_list.html', {'report_bookings': bookings, 'title': 'All Bookings'})

@user_passes_test(lambda u: u.is_staff)
def admin_turf_review(request, turf_id):
    turf = get_object_or_404(Turf.objects.select_related('owner', 'owner__owner_profile').prefetch_related('images', 'sports'), id=turf_id)
    
    # Activity Monitoring
    total_bookings = Booking.objects.filter(turf=turf).count()
    success_bookings = Booking.objects.filter(turf=turf, payment_status='SUCCESS').count()
    cancelled_bookings = Booking.objects.filter(turf=turf, status='CANCELLED').count()
    
    revenue_data = Booking.objects.filter(turf=turf, payment_status='SUCCESS').aggregate(Sum('total_amount'))
    total_revenue = revenue_data['total_amount__sum'] or 0
    
    last_booking = Booking.objects.filter(turf=turf).order_by('-created_at').first()
    
    # Use Analytics Service
    from core.services.analytics import TurfAnalyticsService
    alerts = TurfAnalyticsService.get_turf_alerts(turf)
    logs = TurfAnalyticsService.get_activity_timeline(turf)

    context = {
        'turf': turf,
        'title': f'Review - {turf.name}',
        'total_bookings': total_bookings,
        'success_bookings': success_bookings,
        'cancelled_bookings': cancelled_bookings,
        'total_revenue': total_revenue,
        'last_booking_date': last_booking.created_at if last_booking else None,
        'activity_logs': logs,
        'alerts': alerts,
    }
    return render(request, 'admin/reports/turf_review.html', context)
