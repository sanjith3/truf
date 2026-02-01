from functools import wraps
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.contrib import messages
from .models import PlatformSettings

def ads_required(view_func):
    """
    Decorator for views that checks if Ad Campaigns are globally enabled.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        settings = PlatformSettings.get_settings()
        if not settings.ads_enabled:
            # Allow staff to access even if disabled for owners
            if request.user.is_authenticated and request.user.is_staff:
                return view_func(request, *args, **kwargs)
            
            messages.warning(request, "Ad Campaigns are currently disabled on the platform.")
            return redirect('core:home')
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view
