from django.db import models
from decimal import Decimal
from django.conf import settings

class PlatformSettings(models.Model):
    """
    Singleton model for global platform configurations.
    """
    # Convenience Fee Settings
    convenience_fee_enabled = models.BooleanField(default=True, null=True)
    convenience_fee_type = models.CharField(
        max_length=10,
        choices=[('FLAT', 'Flat Fee'), ('PERCENT', 'Percentage')],
        default='FLAT',
        null=True
    )
    convenience_fee_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('20.00'),
        null=True,
        help_text="Flat amount (₹) or Percentage (%) based on type"
    )

    # Global Commission (Optional future proofing)
    default_commission_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=Decimal('10.00'))

    # Ad Campaign Feature Flag
    ads_enabled = models.BooleanField(default=False, help_text="Master toggle for the Ad Campaign system across the platform.")

    class Meta:
        verbose_name = "Platform Settings"
        verbose_name_plural = "Platform Settings"

    def __str__(self):
        return "Global Platform Settings"

    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        if not self.pk and PlatformSettings.objects.exists():
            return
        return super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, created = cls.objects.get_or_create(id=1)
        return obj


class AdminActionLog(models.Model):
    """
    Audit log for all admin actions on owner applications and turfs.
    """
    ACTION_CHOICES = [
        ('OWNER_APPROVED', 'Owner Application Approved'),
        ('OWNER_REJECTED', 'Owner Application Rejected'),
        ('TURF_APPROVED', 'Turf Approved'),
        ('TURF_REJECTED', 'Turf Rejected'),
        ('TURF_HIDDEN', 'Turf Hidden'),
        ('TURF_SHOWN', 'Turf Made Visible'),
    ]
    
    admin_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='admin_actions'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    target_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='actions_received'
    )
    target_turf = models.ForeignKey(
        'turfs.Turf',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    reason = models.TextField(blank=True, help_text="Reason for rejection or action")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = "Admin Action Log"
        verbose_name_plural = "Admin Action Logs"
    
    def __str__(self):
        return f"{self.admin_user} - {self.get_action_display()} at {self.timestamp}"
