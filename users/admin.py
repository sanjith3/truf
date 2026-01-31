from django.contrib import admin
from .models import CustomUser, TurfOwnerProfile
from core.admin_site import admin_site

class TurfOwnerProfileInline(admin.StackedInline):
    model = TurfOwnerProfile
    can_delete = False
    verbose_name_plural = 'Turf Owner Profile'

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'is_turf_owner', 'is_owner_approved', 'date_joined')
    search_fields = ('phone_number',)
    list_filter = ('is_turf_owner', 'is_owner_approved', 'is_staff')
    inlines = [TurfOwnerProfileInline]
    actions = ['approve_owners']

    def approve_owners(self, request, queryset):
        queryset.update(is_owner_approved=True)
        self.message_user(request, "Selected owners have been approved.")
    approve_owners.short_description = "Approve selected Turf Owners"

class TurfOwnerProfileAdmin(admin.ModelAdmin):
    list_display = ('business_name', 'user', 'city', 'created_at')
    search_fields = ('business_name', 'user__phone_number', 'city')

admin_site.register(CustomUser, CustomUserAdmin)
admin_site.register(TurfOwnerProfile, TurfOwnerProfileAdmin)
