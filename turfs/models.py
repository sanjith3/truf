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
    sports = models.ManyToManyField(SportType, related_name='turfs')
    amenities = models.TextField(blank=True, help_text="Comma separated list of amenities")
    
    is_active = models.BooleanField(default=True)
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
