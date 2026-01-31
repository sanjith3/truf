from django.utils import timezone
from datetime import timedelta
from bookings.models import Booking
from turfs.models import Turf

class TurfAnalyticsService:
    @staticmethod
    def get_turf_alerts(turf):
        alerts = []
        
        # 1. No Bookings Check
        two_weeks_ago = timezone.now().date() - timedelta(days=14)
        recent_bookings = Booking.objects.filter(turf=turf, created_at__gte=two_weeks_ago).count()
        
        if recent_bookings == 0 and turf.is_active:
            alerts.append({
                'type': 'warning',
                'title': 'No Recent Bookings',
                'message': 'No bookings received in the last 14 days. Review visibility settings.'
            })
            
        # 2. High Cancellation Rate
        all_bookings = Booking.objects.filter(turf=turf)
        total_count = all_bookings.count()
        if total_count >= 5:
            cancelled_count = all_bookings.filter(status='CANCELLED').count()
            rate = (cancelled_count / total_count) * 100
            
            if rate > 30:
                alerts.append({
                    'type': 'critical',
                    'title': 'High Cancellation Rate',
                    'message': f'Cancellation rate is {rate:.1f}% ({cancelled_count}/{total_count}).'
                })
        
        # 3. Hidden Turf Traffic (Simulated check)
        # If we had a PageView model, we would check "views > 100 AND is_active=False"
        if not turf.is_active:
             alerts.append({
                'type': 'info',
                'title': 'Turf is Hidden',
                'message': 'This turf is currently inactive and hidden from users.'
            })
            
        return alerts

    @staticmethod
    def get_activity_timeline(turf, limit=10):
        return turf.activity_logs.all()[:limit]
