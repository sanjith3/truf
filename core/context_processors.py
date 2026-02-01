from .models import PlatformSettings

def platform_settings(request):
    """
    Injects global platform settings into all templates.
    """
    settings = PlatformSettings.get_settings()
    return {
        'ads_enabled': settings.ads_enabled,
        'platform_settings': settings
    }
