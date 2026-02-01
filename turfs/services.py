import datetime
from django.utils import timezone
from .models import Turf, TurfClosure, TurfDayAvailability, TurfSlot, EmergencyBlock

class AvailabilityService:
    @staticmethod
    def is_turf_available(turf, target_date):
        """
        Global check for a specific date (not slot specific).
        Check in order:
        1. Turf active
        2. Emergency block
        3. Manual open_today flag (only if target_date is today)
        4. Date-range closures
        5. Day of week availability
        """
        # 1. Active check
        if not turf.is_active:
            return False, "This turf is currently inactive."

        # 2. Emergency Block
        try:
            emergency = turf.emergency_block
            if emergency.is_blocked:
                return False, f"Emergency Closure: {emergency.reason or 'Operational issues.'}"
        except EmergencyBlock.DoesNotExist:
            pass

        # 3. Manual open_today (only for today)
        today = timezone.now().date()
        if target_date == today:
            if not turf.is_open_today:
                return False, f"Closed Today: {turf.closed_reason or 'Daily maintenance.'}"

        # 4. Date-range closures
        closure = TurfClosure.objects.filter(
            turf=turf,
            start_date__lte=target_date,
            end_date__gte=target_date
        ).first()
        if closure:
            return False, f"Closed for maintenance: {closure.reason}"

        # 5. Day availability
        # weekday() is 0 for Monday, 6 for Sunday
        day_avail = TurfDayAvailability.objects.filter(
            turf=turf,
            day_of_week=target_date.weekday()
        ).first()
        if day_avail and not day_avail.is_open:
            return False, "This turf is closed on this day of the week."

        return True, "Available"

    @staticmethod
    def get_slots_for_date(turf, target_date):
        """
        Returns a list of slots with availability status.
        6 AM to 11 PM (Standard).
        """
        from bookings.models import Booking
        
        is_date_avail, reason = AvailabilityService.is_turf_available(turf, target_date)
        
        slots = []
        for h in range(6, 23):
            start_time = datetime.time(h, 0)
            end_time = datetime.time(h+1, 0)
            
            # Check if this specific slot is manually disabled by owner
            slot_meta = TurfSlot.objects.filter(
                turf=turf,
                start_time=start_time,
                end_time=end_time
            ).first()
            
            # Logic: If global date is closed, all slots are closed.
            # If global date is open, check individual slot enabled status.
            is_enabled = is_date_avail
            if is_enabled and slot_meta:
                is_enabled = slot_meta.is_enabled
                
            # Check if already booked
            is_booked = Booking.objects.filter(
                turf=turf,
                booking_date=target_date,
                start_time=start_time,
                status__in=['CONFIRMED', 'PENDING']
            ).exists()
            
            slots.append({
                'start': start_time,
                'end': end_time,
                'is_booked': is_booked,
                'is_enabled': is_enabled,
                'status_label': 'Available' if (is_enabled and not is_booked) else ('Booked' if is_booked else 'Unavailable')
            })
            
        return slots, is_date_avail, reason
