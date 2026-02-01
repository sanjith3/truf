from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
import random
import datetime
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError(_('The Phone Number must be set'))
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))

        return self.create_user(phone_number, password, **extra_fields)

class CustomUser(AbstractUser):
    username = None
    phone_number = models.CharField(_('phone number'), max_length=15, unique=True)
    
    # Turf Owner Workflow Fields
    is_turf_owner = models.BooleanField(default=False)
    is_owner_approved = models.BooleanField(default=False) # Needs admin approval
    owner_application_date = models.DateTimeField(null=True, blank=True)
    
    # OTP Fields for Demo
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone_number

    def generate_demo_otp(self):
        from django.conf import settings
        # STATIC OTP FOR DEBUG MODE TO UNBLOCK USER
        if settings.DEBUG:
            self.otp = "123456"
        else:
            self.otp = str(random.randint(100000, 999999))
            
        self.otp_created_at = timezone.now()
        self.save()
        
        # 1. FILE-BASED FAILSAFE (Check root directory for OTP_ACTUAL.txt)
        try:
            with open("OTP_ACTUAL.txt", "w") as f:
                f.write(f"USER: {self.phone_number}\nOTP: {self.otp}\nTIME: {timezone.now()}\n\nDEBUG_MODE: {'ACTIVE' if settings.DEBUG else 'OFF'}")
        except Exception as e:
            print(f"FAILED TO WRITE OTP FILE: {e}")

        # 2. ULTRA-LOUD TERMINAL BROADCAST
        # Using print(..., flush=True) for immediate visibility across all terminal types
        print("\n" + "="*50)
        print("🚀🚀🚀 TURFSPOT AUTHENTICATION 🚀🚀🚀")
        print(f"DEVICE: {self.phone_number}")
        print(f"OTP:    >>> {self.otp} <<<")
        print(f"MODE:   {'DEBUG (STATIC)' if settings.DEBUG else 'PRODUCTION (RANDOM)'}")
        print("="*50 + "\n", flush=True)
        
        # 3. LOGGING CHANNEL
        import logging
        logger = logging.getLogger('django')
        logger.error(f"OTP_SENT: {self.phone_number} -> {self.otp}")
        
        return self.otp

class TurfOwnerProfile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='owner_profile')
    owner_name = models.CharField(max_length=100, blank=True, help_text="Full name of the owner")
    business_name = models.CharField(max_length=100)
    contact_email = models.EmailField()
    alternate_phone = models.CharField(max_length=15, blank=True)
    gst_number = models.CharField(max_length=20, blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Profile: {self.business_name} ({self.user.phone_number})"
