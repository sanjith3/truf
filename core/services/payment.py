from .base import BasePaymentProvider
import uuid

class DemoPaymentProvider(BasePaymentProvider):
    """A demo payment provider that mimics Razorpay flow."""
    def create_order(self, amount, currency='INR', receipt=None):
        order_id = f"order_{uuid.uuid4().hex[:12]}"
        return {
            "id": order_id,
            "amount": amount,
            "currency": currency,
            "receipt": receipt,
            "status": "created"
        }
    
    def verify_payment(self, payment_id, order_id, signature):
        # In demo mode, we always consider it verified if signature is 'demo_success'
        if signature == 'demo_success':
            return True
        return False
