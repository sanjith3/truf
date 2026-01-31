from django.db import models
from decimal import Decimal
from django.conf import settings
from turfs.models import Turf
import uuid

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('CONFIRMED', 'Confirmed'),
        ('CANCELLED', 'Cancelled'),
        ('COMPLETED', 'Completed'),
    ]

    PAYMENT_STATUS_CHOICES = [
        ('INITIATED', 'Initiated'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('REFUNDED', 'Refunded'),
    ]

    booking_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='bookings')
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name='bookings')
    
    booking_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default='INITIATED')
    
    # Financial Breakdown
    base_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Original turf price")
    convenience_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Platform convenience fee")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="Total payable (Base + Fee)")
    
    # Revenue fields
    commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))
    platform_commission = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'), help_text="10% cut from base_amount")
    owner_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    
    created_at = models.DateTimeField(auto_now_add=True)

    def calculate_fees(self):
        """
        Calculates convenience fees and final total before payment.
        This should be called when the booking is being initialized.
        """
        from core.models import PlatformSettings
        from decimal import Decimal, ROUND_HALF_UP
        settings = PlatformSettings.get_settings()
        
        # Defensive casting to prevent float mismatch errors
        self.base_amount = Decimal(str(self.base_amount or '0.00'))

        if settings.convenience_fee_enabled:
            fee_val = Decimal(str(settings.convenience_fee_value or '0.00'))
            if settings.convenience_fee_type == 'FLAT':
                self.convenience_fee = fee_val
            else:
                self.convenience_fee = (self.base_amount * (fee_val / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
        else:
            self.convenience_fee = Decimal('0.00')
        
        self.total_amount = self.base_amount + self.convenience_fee

    def calculate_commission(self):
        """
        Calculates platform commission and owner earnings based on base_amount.
        Formula: 
        platform_commission = base_amount * (commission_percentage / 100)
        owner_earnings = base_amount - platform_commission
        """
        if self.payment_status == 'SUCCESS':
            from decimal import Decimal, ROUND_HALF_UP
            
            # Defensive casting
            self.base_amount = Decimal(str(self.base_amount or '0.00'))
            self.commission_percentage = Decimal(str(self.commission_percentage or '10.00'))
            
            self.platform_commission = (self.base_amount * (self.commission_percentage / Decimal('100'))).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            self.owner_earnings = (self.base_amount - self.platform_commission).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            return True
        return False

    def save(self, *args, **kwargs):
        # Auto-calculate fees on first save if not set
        if not self.pk and (not self.total_amount or self.total_amount == 0):
            self.calculate_fees()
            
        # Auto-calculate commission if payment is successful
        if self.payment_status == 'SUCCESS':
            self.calculate_commission()
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(fields=['turf', 'booking_date', 'start_time']),
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.booking_id} - {self.turf.name}"
        
    @property
    def short_id(self):
        return str(self.booking_id)[:8] + '...'
