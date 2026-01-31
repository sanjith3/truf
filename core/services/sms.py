from .base import BaseSMSProvider
import random

class ConsoleSMSProvider(BaseSMSProvider):
    """A provider that 'sends' SMS by printing to the console."""
    def send_otp(self, phone_number, otp):
        import logging
        logger = logging.getLogger('django')
        msg = f"SMS GATEWAY SIMULATION: Phone {phone_number} received OTP {otp}"
        print(f"\n[SMS] {msg}\n")
        logger.info(msg)
        return True

class MockSMSProvider(BaseSMSProvider):
    """A mock provider that always succeeds without printing."""
    def send_otp(self, phone_number, otp):
        return True
