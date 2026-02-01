from django.contrib import admin
from .models import PlatformSettings, AdminActionLog
from .admin_site import admin_site

@admin.register(PlatformSettings, site=admin_site)
class PlatformSettingsAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'ads_enabled', 'convenience_fee_enabled', 'convenience_fee_type', 'convenience_fee_value')
    
    fieldsets = (
        ('Feature Rollout', {
            'fields': ('ads_enabled',),
            'description': 'Master toggles for major platform modules.'
        }),
        ('Revenue & Checkout', {
            'fields': ('convenience_fee_enabled', 'convenience_fee_type', 'convenience_fee_value', 'default_commission_percentage'),
        }),
    )

    def has_add_permission(self, request):
        # Only allow one instance
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(AdminActionLog, site=admin_site)
class AdminActionLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'admin_user', 'action', 'target_user', 'short_reason')
    list_filter = ('action', 'timestamp')
    search_fields = ('admin_user__phone_number', 'target_user__phone_number', 'reason')
    readonly_fields = ('admin_user', 'action', 'target_user', 'target_turf', 'reason', 'timestamp')
    date_hierarchy = 'timestamp'
    
    def short_reason(self, obj):
        return obj.reason[:50] + '...' if len(obj.reason) > 50 else obj.reason
    short_reason.short_description = 'Reason'
    
    def has_add_permission(self, request):
        return False  # Logs are created automatically
    
    def has_delete_permission(self, request, obj=None):
        return False  # Preserve audit trail
