from django.shortcuts import render, get_object_or_404, redirect
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Turf, TurfImage, TurfDayAvailability, TurfSlot, EmergencyBlock, TurfClosure
from .forms import TurfForm, TurfImageForm

from django.utils import timezone

from core.services.location import LocationService

from django.db.models import Value
from django.db.models.functions import Coalesce

def turf_list(request):
    from subscriptions.models import OwnerSubscription
    from django.db import models
    
    # Optimized query with real-time subscription status check
    # Only ACTIVE and NON-EXPIRED subscriptions contribute to ranking
    now = timezone.now()
    turfs = Turf.objects.filter(is_active=True).annotate(
        priority_tier=Coalesce(
            models.Subquery(
                OwnerSubscription.objects.filter(
                    owner=models.OuterRef('owner'),
                    status='ACTIVE',
                    end_date__gt=now
                ).values('plan__tier')[:1]
            ), 
            Value(0)
        )
    ).order_by('-priority_tier', '-created_at').select_related('owner')
    
    # Location Search
    lat = request.GET.get('lat')
    lon = request.GET.get('long')
    radius = request.GET.get('radius', 5)
    
    # Quick Filters
    q_filter = request.GET.get('filter')
    if q_filter == 'price_low':
        turfs = turfs.filter(price_per_hour__lte=1000)
    elif q_filter == '5v5':
        turfs = turfs.filter(sports__name__icontains='5v5')
    
    # City Search
    city = request.GET.get('city')
    if city:
        turfs = turfs.filter(city__icontains=city)
        
    # Apply Radius Search if Lat/Long exists
    if lat and lon:
        try:
            turfs = LocationService.get_nearby_turfs(
                turfs, float(lat), float(lon), float(radius)
            )
        except (ValueError, TypeError):
            pass
            
    # Professional UX: Attach "Next Available Slot" to each turf
    from .services import AvailabilityService
    import datetime
    target_date = timezone.now().date()
    
    for turf in turfs:
        slots, is_avail, reason = AvailabilityService.get_slots_for_date(turf, target_date)
        next_slot = next((s for s in slots if s['is_enabled'] and not s['is_booked']), None)
        turf.next_available_slot = next_slot
        turf.show_closed_badge = not is_avail

    # Fetch Sponsored Ads for LISTING placement
    from ads.services import AdService
    sponsored_ads = AdService.get_served_ads('LISTING', city=city, limit=2)
    
    # Record impressions
    for ad in sponsored_ads:
        AdService.record_impression(ad, user=request.user if request.user.is_authenticated else None, city=city)
            
    context = {
        'turfs': turfs,
        'sponsored_ads': sponsored_ads,
        'has_location': bool(lat and lon),
        'active_filter': q_filter
    }
    return render(request, 'turfs/turf_list.html', context)

def turf_detail(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id, is_active=True)
    
    amenities_list = []
    if turf.amenities:
        amenities_list = [a.strip() for a in turf.amenities.split(',') if a.strip()]

    context = {
        'turf': turf,
        'amenities_list': amenities_list
    }
    return render(request, 'turfs/turf_detail.html', context)

@login_required
def add_turf(request):
    # Ensure user is an approved owner
    if not request.user.is_turf_owner or not request.user.is_owner_approved:
        messages.error(request, "Only approved owners can add turfs.")
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = TurfForm(request.POST)
        if form.is_valid():
            turf = form.save(commit=False)
            turf.owner = request.user
            turf.is_active = False # Requires admin approval for new turfs too usually, or auto-approve if owner is trusted
            turf.save()
            form.save_m2m() # Save sports
            messages.success(request, f"Turf '{turf.name}' added successfully! It will be visible after review.")
            return redirect('users:dashboard')
    else:
        form = TurfForm()
    
    return render(request, 'turfs/add_edit_turf.html', {'form': form, 'title': 'Add New Turf'})

@login_required
def edit_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id, owner=request.user)
    
    if request.method == 'POST':
        form = TurfForm(request.POST, instance=turf)
        if form.is_valid():
            form.save()
            messages.success(request, f"Turf '{turf.name}' updated successfully!")
            return redirect('users:dashboard')
    else:
        form = TurfForm(instance=turf)
    
    return render(request, 'turfs/add_edit_turf.html', {'form': form, 'title': f'Edit {turf.name}', 'turf': turf})

@login_required
def manage_turf_images(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id, owner=request.user)
    
    if request.method == 'POST':
        form = TurfImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = TurfImage(
                turf=turf,
                image=form.cleaned_data['image'],
                is_cover=form.cleaned_data['is_cover']
            )
            # If this is cover, unset others
            if img.is_cover:
                turf.images.filter(is_cover=True).update(is_cover=False)
            img.save()
            messages.success(request, "Image uploaded successfully!")
            return redirect('turfs:manage_images', turf_id=turf.id)
    else:
        form = TurfImageForm()
    
    images = turf.images.all()
    return render(request, 'turfs/manage_images.html', {'turf': turf, 'images': images, 'form': form})

@login_required
def turf_operations(request, turf_id):
    """
    Main Management Dashboard for Turf Operations.
    """
    turf = get_object_or_404(Turf, id=turf_id, owner=request.user)
    
    # Ensure emergency block object exists
    EmergencyBlock.objects.get_or_create(turf=turf)
    
    # POST Handlers for different operation cards
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'update_day':
            day_id = int(request.POST.get('day_of_week'))
            is_open = request.POST.get('is_open') == 'on'
            TurfDayAvailability.objects.update_or_create(
                turf=turf, day_of_week=day_id, defaults={'is_open': is_open}
            )
            messages.success(request, "Schedule updated.")
            
        elif action == 'toggle_slot':
            start = request.POST.get('start_time')
            end = request.POST.get('end_time')
            enabled = request.POST.get('is_enabled') == 'on'
            TurfSlot.objects.update_or_create(
                turf=turf, start_time=start, end_time=end, defaults={'is_enabled': enabled}
            )
            messages.info(request, "Slot status updated.")

        elif action == 'add_closure':
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            reason = request.POST.get('reason')
            TurfClosure.objects.create(
                turf=turf, start_date=start_date, end_date=end_date, reason=reason
            )
            messages.success(request, f"Temporary closure scheduled from {start_date}.")

        return redirect('turfs:operations', turf_id=turf.id)

    # Context Data
    day_avail = {d.day_of_week: d.is_open for d in turf.day_availability.all()}
    week_days = []
    for i, name in [(0, 'Monday'), (1, 'Tuesday'), (2, 'Wednesday'), (3, 'Thursday'), (4, 'Friday'), (5, 'Saturday'), (6, 'Sunday')]:
        week_days.append({
            'id': i,
            'name': name,
            'is_open': day_avail.get(i, True) # Default open if not set
        })
        
    # Standard slots for management (6 AM to 11 PM)
    slots_meta = {s.start_time.strftime('%H:%M'): s.is_enabled for s in turf.custom_slots.all()}
    slots = []
    for h in range(6, 23):
        t_start = datetime.time(h, 0)
        t_end = datetime.time(h+1, 0)
        start_str = t_start.strftime('%H:%M')
        
        slots.append({
            'start': t_start,
            'end': t_end,
            'is_enabled': slots_meta.get(start_str, True)
        })

    context = {
        'turf': turf,
        'week_days': week_days,
        'slots': slots,
        'closures': turf.closures.filter(end_date__gte=timezone.now().date()).order_by('start_date')
    }
    return render(request, 'turfs/owner_operations.html', context)

@login_required
def toggle_today_status(request, turf_id):
    if request.method == 'POST':
        turf = get_object_or_404(Turf, id=turf_id, owner=request.user)
        turf.is_open_today = not turf.is_open_today
        turf.closed_reason = request.POST.get('reason', '')
        turf.save()
        status = "OPEN" if turf.is_open_today else "CLOSED"
        messages.warning(request, f"Facility status for TODAY set to {status}.")
    return redirect('turfs:operations', turf_id=turf_id)

@login_required
def toggle_emergency_block(request, turf_id):
    if request.method == 'POST':
        turf = get_object_or_404(Turf, id=turf_id, owner=request.user)
        block, _ = EmergencyBlock.objects.get_or_create(turf=turf)
        block.is_blocked = not block.is_blocked
        block.reason = request.POST.get('reason', 'Operational Emergency')
        block.save()
        
        if block.is_blocked:
            messages.error(request, "🚨 EMERGENCY BLOCK ACTIVE. No bookings can be made.")
        else:
            messages.success(request, "Emergency block deactivated. Operations resumed.")
    return redirect('turfs:operations', turf_id=turf_id)
