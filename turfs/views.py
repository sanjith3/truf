from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Turf, TurfImage
from .forms import TurfForm, TurfImageForm

from core.services.location import LocationService

from django.db.models import Value
from django.db.models.functions import Coalesce

def turf_list(request):
    from subscriptions.models import OwnerSubscription
    from django.utils import timezone
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
            
    # Fetch Sponsored Ads for LISTING placement
    from ads.services import AdService
    sponsored_ads = AdService.get_served_ads('LISTING', city=city, limit=2)
    
    # Record impressions
    for ad in sponsored_ads:
        AdService.record_impression(ad, user=request.user if request.user.is_authenticated else None, city=city)
            
    context = {
        'turfs': turfs,
        'sponsored_ads': sponsored_ads,
        'has_location': bool(lat and lon)
    }
    return render(request, 'turfs/turf_list.html', context)

def turf_detail(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id, is_active=True)
    context = {
        'turf': turf
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
