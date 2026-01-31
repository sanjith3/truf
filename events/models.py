from django.db import models
from django.conf import settings
from turfs.models import SportType
from decimal import Decimal

class Tournament(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved & Live'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    name = models.CharField(max_length=200)
    sport = models.ForeignKey(SportType, on_delete=models.CASCADE)
    city = models.CharField(max_length=100)
    description = models.TextField()
    
    organizer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='organized_tournaments')
    
    start_date = models.DateField()
    end_date = models.DateField()
    
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, help_text="Registration fee per team/player")
    max_registrations = models.PositiveIntegerField(default=16)
    
    # Revenue Configuration
    listing_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="One-time fee paid by organizer to list")
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'), help_text="Platform cut from each entry fee")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    is_paid_listing = models.BooleanField(default=False, help_text="Check if organizer paid the listing fee")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def total_expected_revenue(self):
        # Listing fee + (commission per registration * max spots)
        from .models import TournamentRegistration
        actual_registrations = self.registrations.filter(payment_status='SUCCESS').count()
        reg_revenue = Decimal(actual_registrations) * (self.entry_fee * (self.commission_percentage / Decimal('100')))
        return self.listing_fee + reg_revenue

    def __str__(self):
        return self.name

class TournamentRegistration(models.Model):
    PAYMENT_STATUS = [
        ('PENDING', 'Pending'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
    ]

    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE, related_name='registrations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    team_name = models.CharField(max_length=100, blank=True)
    
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='PENDING')
    registered_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.platform_commission:
            self.platform_commission = self.amount_paid * (self.tournament.commission_percentage / Decimal('100'))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.phone_number} - {self.tournament.name}"
