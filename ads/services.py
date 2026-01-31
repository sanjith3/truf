from .models import AdCampaign
from django.utils import timezone
from django.db.models import Q, F
from decimal import Decimal

class AdService:
    @staticmethod
    def get_served_ads(placement, city=None, limit=1):
        """
        Fetches production-eligible ads.
        Filters by:
        - Status == ACTIVE
        - Schedule (Start/End date)
        - Budget (Spent < Total)
        """
        now = timezone.now()
        
        # Core eligibility filters
        qs = AdCampaign.objects.filter(
            status='ACTIVE',
            placement=placement,
            start_date__lte=now,
            end_date__gte=now,
            spent_amount__lt=F('total_budget')
        )
        
        # Optional: Geo-targeting
        if city:
            # Note: We assume global ads have target_city as null or empty
            # If target_city is present, it must match.
            pass # Placeholder for more complex geo logic if desired
            
        return qs.order_by('?')[:limit]

    @staticmethod
    def record_impression(campaign, user=None, city=None):
        """
        Service wrapper to record impression. 
        Note: The heavy lifting is done in the model method to ensure atomicity.
        """
        return campaign.track_impression(user=user, city=city)

    @staticmethod
    def record_click(campaign, user=None):
        """
        Service wrapper to record click.
        Handles the redirect and billing logic.
        """
        return campaign.track_click(user=user)
