from django.contrib import admin
from .models import AdCampaign, AdImpression, AdClick
from django.db.models import Sum

@admin.register(AdCampaign)
class AdCampaignAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'advertiser_name', 
        'status', 
        'cost_model', 
        'spent_amount', 
        'total_budget', 
        'impressions', 
        'clicks', 
        'get_ctr'
    )
    list_filter = ('status', 'ad_type', 'cost_model', 'placement')
    search_fields = ('title', 'advertiser_name', 'advertiser__phone_number')
    actions = ['approve_campaigns', 'pause_campaigns', 'mark_completed']
    readonly_fields = ('spent_amount', 'impressions', 'clicks')

    fieldsets = (
        ('Campaign Info', {
            'fields': (('title', 'advertiser_name'), 'advertiser', ('ad_type', 'placement'), 'redirect_url', 'image')
        }),
        ('Schedule', {
            'fields': (('start_date', 'end_date'), 'status')
        }),
        ('Budget & Revenue', {
            'fields': ('cost_model', 'cost_per_unit', ('daily_budget', 'total_budget'), 'spent_amount')
        }),
        ('Performance', {
            'fields': (('impressions', 'clicks'),)
        }),
    )

    def get_ctr(self, obj):
        return f"{obj.ctr:.2f}%"
    get_ctr.short_description = 'CTR'

    def approve_campaigns(self, request, queryset):
        queryset.update(status='ACTIVE')
        self.message_user(request, "Selected campaigns are now live.")
    approve_campaigns.short_description = "Approve selected (Go Live)"

    def pause_campaigns(self, request, queryset):
        queryset.update(status='PAUSED')
    pause_campaigns.short_description = "Pause selected"

    def mark_completed(self, request, queryset):
        queryset.update(status='COMPLETED')
    mark_completed.short_description = "Mark as COMPLETED"

@admin.register(AdImpression)
class AdImpressionAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'user', 'city', 'timestamp')
    list_filter = ('campaign', 'city')

@admin.register(AdClick)
class AdClickAdmin(admin.ModelAdmin):
    list_display = ('campaign', 'user', 'timestamp')
    list_filter = ('campaign',)
