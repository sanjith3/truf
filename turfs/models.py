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
    
    price_per_hour = models.DecimalField(max_digits=10, decimal_places=2)
    sports = models.ManyToManyField(SportType, related_name='turfs')
    amenities = models.TextField(blank=True, help_text="Comma separated list of amenities")
    
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class TurfImage(models.Model):
    turf = models.ForeignKey(Turf, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='turf_images/')
    is_cover = models.BooleanField(default=False)

    def __str__(self):
        return f"Image for {self.turf.name}"
