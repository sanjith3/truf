from django.contrib import admin
from .models import Turf, TurfImage, SportType
from core.admin_site import admin_site

class TurfImageInline(admin.TabularInline):
    model = TurfImage
    extra = 1

class TurfAdmin(admin.ModelAdmin):
    list_display = ('name', 'city', 'owner', 'price_per_hour', 'is_active')
    list_filter = ('is_active', 'city', 'sports')
    search_fields = ('name', 'city')
    inlines = [TurfImageInline]
    actions = ['approve_turfs', 'deactivate_turfs']

    def approve_turfs(self, request, queryset):
        queryset.update(is_active=True)
    approve_turfs.short_description = "Approve selected turfs"

    def deactivate_turfs(self, request, queryset):
        queryset.update(is_active=False)
    deactivate_turfs.short_description = "Deactivate selected turfs"

class SportTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin_site.register(Turf, TurfAdmin)
admin_site.register(SportType, SportTypeAdmin)
