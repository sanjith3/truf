from django.db.models import Sum
from .models import Tournament, TournamentRegistration
from decimal import Decimal

class EventService:
    @staticmethod
    def get_active_tournaments(city=None):
        qs = Tournament.objects.filter(status='APPROVED')
        if city:
            qs = qs.filter(city__icontains=city)
        return qs.order_by('start_date')

    @staticmethod
    def register_team(tournament, user, team_name):
        """
        Creates a registration entry. 
        In production, this would integrate with payment flow.
        """
        if tournament.registrations.filter(payment_status='SUCCESS').count() >= tournament.max_registrations:
            return None, "Tournament is full"

        registration = TournamentRegistration.objects.create(
            tournament=tournament,
            user=user,
            team_name=team_name,
            amount_paid=tournament.entry_fee,
            payment_status='PENDING'
        )
        return registration, None

    @staticmethod
    def get_platform_event_revenue():
        """
        Aggregates listing fees + registration commissions.
        """
        listing_revenue = Tournament.objects.filter(is_paid_listing=True).aggregate(Sum('listing_fee'))['listing_fee__sum'] or Decimal('0.00')
        registration_commission = TournamentRegistration.objects.filter(payment_status='SUCCESS').aggregate(Sum('platform_commission'))['platform_commission__sum'] or Decimal('0.00')
        
        return {
            'listing_revenue': listing_revenue,
            'commission_revenue': registration_commission,
            'total_event_revenue': listing_revenue + registration_commission
        }
