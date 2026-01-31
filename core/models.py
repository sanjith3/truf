from django.db import models
from decimal import Decimal

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
