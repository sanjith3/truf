from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class SportType(models.Model):
    name = models.CharField(max_length=50)
    icon = models.CharField(max_length=50, blank=True, help_text="FontAwesome icon class")

    def __str__(self):
        return self.name

class Turf(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='turfs')
    name = models.CharField(max_length=200)
    description = models.TextField()
    address = models.TextField()
    city = models.CharField(max_length=100)
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    map_share_url = models.URLField(blank=True, null=True, help_text="Google Maps Share Link")
    
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    rules = models.TextField(blank=True, help_text="Venue rules (e.g. No metal studs, reach 15 min early)")
    sports = models.ManyToManyField(SportType, related_name='turfs')
    amenities = models.TextField(blank=True, help_text="Comma separated list of amenities")
    
    is_active = models.BooleanField(default=True)
    is_open_today = models.BooleanField(default=True, help_text="Manual toggle for today's status")
    closed_reason = models.CharField(max_length=255, blank=True, null=True, help_text="Public reason for today's closure")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TurfImage(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='turf_images/', max_length=500)
    is_cover = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.turf.name}"

class TurfVideo(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='turf_videos/', help_text="Small promo video (max 15s)", max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Video for {self.turf.name}"

class TurfActivityLog(models.Model):
    EVENT_TYPES = [
        ('BOOKING', 'New Booking'),
        ('CANCELLATION', 'Booking Cancelled'),
        ('STATUS_CHANGE', 'Status Changed'),
        ('PRICE_CHANGE', 'Price Updated'),
        ('INFO', 'Information'),
    ]
    
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name='activity_logs')
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField()
    triggered_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.turf.name} - {self.event_type}"

class TurfClosure(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name='closures')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.turf.name} closure: {self.start_date} to {self.end_date}"

class TurfDayAvailability(models.Model):
    DAYS = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name='day_availability')
    day_of_week = models.IntegerField(choices=DAYS)
    is_open = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ('turf', 'day_of_week')

    def __str__(self):
        return f"{self.turf.name} - {self.get_day_of_week_display()}: {'Open' if self.is_open else 'Closed'}"

class TurfSlot(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name='custom_slots')
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_enabled = models.BooleanField(default=True)

    class Meta:
        unique_together = ('turf', 'start_time', 'end_time')

    def __str__(self):
        return f"{self.turf.name} slot: {self.start_time}-{self.end_time} ({'Enabled' if self.is_enabled else 'Disabled'})"

class EmergencyBlock(models.Model):
    turf = models.OneToOneField(Turf, on_delete=models.CASCADE, related_name='emergency_block')
    is_blocked = models.BooleanField(default=False)
    blocked_at = models.DateTimeField(auto_now=True)
    reason = models.TextField(blank=True)

    def __str__(self):
        return f"Emergency Block for {self.turf.name}: {'ACTIVE' if self.is_blocked else 'OFF'}"
