from django.contrib import admin
from .models import PlatformSettings
from .admin_site import admin_site

@admin.register(PlatformSettings, site=admin_site)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'convenience_fee_enabled', 'convenience_fee_type', 'convenience_fee_value')
    
    def has_add_permission(self, request):
        # Only allow one instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False
