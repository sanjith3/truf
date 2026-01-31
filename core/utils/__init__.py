from django.conf import settings
from django.utils.module_loading import import_string

def get_sms_provider():
    """Returns an instance of the configured SMS provider."""
    return import_string(settings.SMS_PROVIDER)()

def get_payment_provider():
    """Returns an instance of the configured Payment provider."""
    return import_string(settings.PAYMENT_PROVIDER)()
