from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum
from .models import AdCampaign
from .forms import AdCampaignForm
from .services import AdService
from decimal import Decimal
from core.decorators import ads_required

def ad_redirect(request, ad_id):
    """
    Primary endpoint for ad clicks. 
    1. Tracking click
    2. Calculating CPC if applicable
    3. Redirecting user to landing page
    """
    ad = get_object_or_404(AdCampaign, id=ad_id)
    user = request.user if request.user.is_authenticated else None
    
    # Logic is encapsulated in the service/model tracker
    AdService.record_click(ad, user)
    
    return redirect(ad.redirect_url)

@login_required
@ads_required
@user_passes_test(lambda u: u.is_staff or u.is_turf_owner)
def advertiser_dashboard(request):
    """
    Advertiser-facing stats.
    Calculates platform-verified totals from the database.
    """
    campaigns = AdCampaign.objects.filter(advertiser=request.user).order_by('-created_at')
    
    stats = campaigns.aggregate(
        total_spend=Sum('spent_amount'),
        total_impressions=Sum('impressions'),
        total_clicks=Sum('clicks')
    )
    
    # Precision handling for template display
    context = {
        'campaigns': campaigns,
        'total_spend': stats['total_spend'] or Decimal('0.00'),
        'total_impressions': stats['total_impressions'] or 0,
        'total_clicks': stats['total_clicks'] or 0,
    }
    return render(request, 'ads/advertiser_dashboard.html', context)

@login_required
@ads_required
@user_passes_test(lambda u: u.is_staff or u.is_turf_owner)
def campaign_create(request):
    if request.method == 'POST':
        form = AdCampaignForm(request.POST, request.FILES)
        if form.is_valid():
            campaign = form.save(commit=False)
            campaign.advertiser = request.user
            campaign.status = 'PENDING_APPROVAL'
            campaign.save()
            messages.success(request, "Your campaign has been submitted for admin review.")
            return redirect('ads:dashboard')
    else:
        form = AdCampaignForm()
    
    return render(request, 'ads/campaign_form.html', {'form': form, 'title': 'Launch New Campaign'})

@login_required
@ads_required
@user_passes_test(lambda u: u.is_staff or u.is_turf_owner)
def campaign_detail(request, campaign_id):
    """Detailed analytics for a specific campaign."""
    if request.user.is_staff:
        campaign = get_object_or_404(AdCampaign, id=campaign_id)
    else:
        campaign = get_object_or_404(AdCampaign, id=campaign_id, advertiser=request.user)
    return render(request, 'ads/campaign_detail.html', {'campaign': campaign})
