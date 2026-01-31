from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Turf, TurfActivityLog
from bookings.models import Booking

@receiver(pre_save, sender=Turf)
def track_turf_changes(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_turf = Turf.objects.get(pk=instance.pk)
            
            # Price Change
            if old_turf.price_per_hour != instance.price_per_hour:
                TurfActivityLog.objects.create(
                    turf=instance,
                    event_type='PRICE_CHANGE',
                    description=f"Price updated from {old_turf.price_per_hour} to {instance.price_per_hour}",
                    triggered_by=instance.owner 
                )
            
            # Status Change
            if old_turf.is_active != instance.is_active:
                status = "Active" if instance.is_active else "Inactive"
                TurfActivityLog.objects.create(
                    turf=instance,
                    event_type='STATUS_CHANGE',
                    description=f"Turf status changed to {status}",
                    triggered_by=None # System/Admin action usually
                )
        except Turf.DoesNotExist:
            pass

@receiver(post_save, sender=Booking)
def log_booking_creation(sender, instance, created, **kwargs):
    if created:
        TurfActivityLog.objects.create(
            turf=instance.turf,
            event_type='BOOKING',
            description=f"Booking #{instance.short_id} created",
            triggered_by=instance.user
        )

@receiver(pre_save, sender=Booking)
def log_booking_cancellation(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_booking = Booking.objects.get(pk=instance.pk)
            if old_booking.status != 'CANCELLED' and instance.status == 'CANCELLED':
                 TurfActivityLog.objects.create(
                    turf=instance.turf,
                    event_type='CANCELLATION',
                    description=f"Booking #{instance.short_id} cancelled",
                    triggered_by=instance.user
                )
        except Booking.DoesNotExist:
            pass
