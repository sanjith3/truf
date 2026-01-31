from .base import BaseSMSProvider
import random

class ConsoleSMSProvider(BaseSMSProvider):
    """A provider that 'sends' SMS by printing to the console."""
    def send_otp(self, phone_number, otp):
        print(f"\n" + "="*40)
        print(f" SMS SENT TO: {phone_number}")
        print(f" MESSAGE: Your TurfSpot OTP is {otp}")
        print("="*40 + "\n")
        return True

class MockSMSProvider(BaseSMSProvider):
    """A mock provider that always succeeds without printing."""
    def send_otp(self, phone_number, otp):
        return True
