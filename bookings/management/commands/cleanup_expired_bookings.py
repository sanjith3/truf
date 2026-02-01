"""
Django management command to clean up expired bookings.

CRITICAL SECURITY FIX: Releases slots that were reserved but payment not completed within 10 minutes.

Usage:
    python manage.py cleanup_expired_bookings

Recommended: Run this every 5 minutes via cron or Celery Beat
    */5 * * * * cd /path/to/project && python manage.py cleanup_expired_bookings
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from bookings.models import Booking


class Command(BaseCommand):
    help = 'Cancels PENDING bookings that have expired (>10 minutes old)'

    def handle(self, *args, **options):
        now = timezone.now()
        
        # Find all PENDING bookings where expires_at has passed
        expired_bookings = Booking.objects.filter(
            status='PENDING',
            expires_at__lt=now
        )
        
        count = expired_bookings.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No expired bookings found.'))
            return
        
        # Cancel all expired bookings
        for booking in expired_bookings:
            booking.status = 'CANCELLED'
            booking.payment_status = 'FAILED'
            booking.save()
            
            self.stdout.write(
                self.style.WARNING(
                    f'Cancelled booking {booking.booking_id} '
                    f'(Turf: {booking.turf.name}, Slot: {booking.start_time}, '
                    f'Expired: {booking.expires_at})'
                )
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully cancelled {count} expired booking(s). Slots released.'
            )
        )
