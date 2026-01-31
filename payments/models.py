from django.db import models
from bookings.models import Booking

class DemoPayment(models.Model):
    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='payment')
    transaction_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Store fake gateway response
    gateway_response = models.JSONField(default=dict)

    def __str__(self):
        return f"Payment {self.transaction_id} for {self.booking.booking_id}"
