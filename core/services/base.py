class BaseSMSProvider:
    """Base interface for SMS providers."""
    def send_otp(self, phone_number, otp):
        raise NotImplementedError("Subclasses must implement send_otp")

class BasePaymentProvider:
    """Base interface for payment providers."""
    def create_order(self, amount, currency='INR', receipt=None):
        raise NotImplementedError("Subclasses must implement create_order")
    
    def verify_payment(self, payment_id, order_id, signature):
        raise NotImplementedError("Subclasses must implement verify_payment")
