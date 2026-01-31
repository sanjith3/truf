from django.db import models
from django.conf import settings
from decimal import Decimal
from django.utils import timezone

class AdCampaign(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('PAUSED', 'Paused'),
        ('COMPLETED', 'Completed'),
        ('PENDING_APPROVAL', 'Pending Approval'),
    ]

    AD_TYPE_CHOICES = [
        ('BANNER', 'Banner Ad'),
        ('SPONSORED_TURF', 'Sponsored Turf Listing'),
        ('PROMOTION_CARD', 'Featured Promotion Card'),
    ]

    COST_MODEL_CHOICES = [
        ('CPM', 'Cost Per Thousand Impressions (CPM)'),
        ('CPC', 'Cost Per Click (CPC)'),
        ('FIXED', 'Fixed Price (per Day)'),
    ]

    PLACEMENT_CHOICES = [
        ('HOME', 'Home Page'),
        ('SEARCH', 'Search Results'),
        ('LISTING', 'Turf Listing Detail'),
    ]

    advertiser = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='ad_campaigns',
        null=True,
        blank=True
    )
    advertiser_name = models.CharField(max_length=255, help_text="Business Name for the ad")
    
    ad_type = models.CharField(max_length=50, choices=AD_TYPE_CHOICES)
    placement = models.CharField(max_length=50, choices=PLACEMENT_CHOICES)
    
    title = models.CharField(max_length=255)
    image = models.ImageField(upload_to='ads/creatives/', blank=True, null=True)
    redirect_url = models.URLField()
    
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    daily_budget = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_budget = models.DecimalField(max_digits=10, decimal_places=2)
    
    cost_model = models.CharField(max_length=10, choices=COST_MODEL_CHOICES, default='CPC')
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2, help_text="Cost per Click, 1000 Impressions, or Day")
    
    spent_amount = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Real-time counters
    impressions = models.PositiveIntegerField(default=0)
    clicks = models.PositiveIntegerField(default=0)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING_APPROVAL')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.advertiser_name})"

    @property
    def ctr(self):
        """Calculate Click-Through Rate as a percentage."""
        if self.impressions == 0:
            return 0.0
        return (self.clicks / self.impressions) * 100

    @property
    def remaining_budget(self):
        return max(Decimal('0.00'), self.total_budget - self.spent_amount)

    @property
    def budget_utilization_percentage(self):
        """Calculate what percentage of the total budget has been spent."""
        if not self.total_budget or self.total_budget <= 0:
            return 0
        percentage = (self.spent_amount / self.total_budget) * 100
        return min(100, float(percentage))

    def is_runnable(self):
        """Check if ad should be served based on real production logic."""
        now = timezone.now()
        return (
            self.status == 'ACTIVE' and 
            self.start_date <= now <= self.end_date and
            self.spent_amount < self.total_budget
        )

    def track_impression(self, user=None, city=None):
        """Record impression and update spend in one atomic operation."""
        if not self.is_runnable():
            return False
            
        AdImpression.objects.create(campaign=self, user=user, city=city)
        self.impressions += 1
        
        if self.cost_model == 'CPM':
            # CPM = Cost per 1000 impressions
            increment = (self.cost_per_unit / Decimal('1000'))
            self.spent_amount += increment

        self._check_budget_limits()
        self.save()
        return True

    def track_click(self, user=None):
        """Record click and update spend based on CPC model."""
        if not self.is_runnable():
            return False
            
        AdClick.objects.create(campaign=self, user=user)
        self.clicks += 1
        
        if self.cost_model == 'CPC':
            self.spent_amount += self.cost_per_unit
            
        self._check_budget_limits()
        self.save()
        return True

    def _check_budget_limits(self):
        """Auto-stop if budget is reached."""
        if self.spent_amount >= self.total_budget:
            self.status = 'COMPLETED'

class AdImpression(models.Model):
    campaign = models.ForeignKey(AdCampaign, on_delete=models.CASCADE, related_name='impression_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

class AdClick(models.Model):
    campaign = models.ForeignKey(AdCampaign, on_delete=models.CASCADE, related_name='click_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
