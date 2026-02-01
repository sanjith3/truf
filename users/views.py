from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.db import transaction
from .models import CustomUser, TurfOwnerProfile
from turfs.models import Turf, SportType, TurfImage, TurfVideo

User = get_user_model()

# ... Login/OTP Views (unchanged) ...
def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        if phone:
            user, created = User.objects.get_or_create(phone_number=phone)
            otp = user.generate_demo_otp()
            request.session['auth_user_id'] = user.id
            if settings.DEBUG:
                messages.success(request, f"OTP Sent! [DEMO MODE: OTP is {otp}]")
            else:
                messages.success(request, f"OTP Sent to {phone}. Check Console Logs!")
            return redirect('users:verify_otp')
        else:
            messages.error(request, "Please enter a valid phone number.")
    return render(request, 'users/login.html')

def verify_otp_view(request):
    user_id = request.session.get('auth_user_id')
    if not user_id: return redirect('users:login')
    
    if request.method == 'POST':
        otp_input = request.POST.get('otp')
        try:
            user = User.objects.get(id=user_id)
            
            # CRITICAL SECURITY: Check OTP expiration (10 minutes)
            if user.otp_created_at:
                from datetime import timedelta
                otp_age = timezone.now() - user.otp_created_at
                if otp_age > timedelta(minutes=10):
                    user.otp = None  # Invalidate expired OTP
                    user.save()
                    messages.error(request, "OTP expired. Please request a new one.")
                    return redirect('users:login')
            
            if user.otp == otp_input:
                user.otp = None 
                user.save()
                login(request, user)
                del request.session['auth_user_id']
                if user.is_turf_owner and not user.is_owner_approved:
                     messages.warning(request, "Your owner account is pending approval.")
                return redirect('users:dashboard')
            else:
                messages.error(request, "Invalid OTP.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")
            return redirect('users:login')
    return render(request, 'users/verify_otp.html')

def logout_view(request):
    logout(request)
    return redirect('users:login')

@login_required
def dashboard_view(request):
    bookings = request.user.bookings.all().order_by('-created_at')
    context = {'bookings': bookings}
    
    if request.user.is_turf_owner:
        if not request.user.is_owner_approved:
            context['pending_approval'] = True
            return render(request, 'users/owner_dashboard.html', context)
        else:
            turfs = request.user.turfs.all()
            context['turfs'] = turfs
            return render(request, 'users/owner_dashboard.html', context)
    return render(request, 'users/dashboard.html', context)

from core.utils.geo import GoogleMapsParser

@login_required
def register_as_owner(request):
    if request.method == 'POST':
        # 1. Collect Form Data
        owner_name = request.POST.get('owner_name', '')
        business_name = request.POST.get('business_name')
        contact_email = request.POST.get('contact_email')
        city = request.POST.get('city')
        address = request.POST.get('address')
        zip_code = request.POST.get('zip_code')
        
        # New Turf Fields
        description = request.POST.get('description', '')
        price_per_hour = request.POST.get('price_per_hour')
        map_share_url = request.POST.get('map_share_url')
        sport_ids = request.POST.getlist('sports')

        # Location Extraction Logic
        latitude, longitude = None, None
        if map_share_url:
            if not GoogleMapsParser.is_valid_link(map_share_url):
                messages.error(request, "Invalid Google Maps link format. Please follow the instructions to get a share link.")
                return render(request, 'users/register_owner.html', {'sports': SportType.objects.all(), 'form_data': request.POST})
            
            latitude, longitude = GoogleMapsParser.extract_lat_lon(map_share_url)
            
            if latitude is None or longitude is None:
                messages.error(request, "Could not automatically detect coordinates. Please drop a specific pin on the map location and share that link.")
                return render(request, 'users/register_owner.html', {'sports': SportType.objects.all(), 'form_data': request.POST})

        with transaction.atomic():
            # 2. Update User Flags
            request.user.is_turf_owner = True
            request.user.is_owner_approved = False  
            request.user.owner_application_date = timezone.now()
            request.user.save()
            
            # 3. Create or Update Profile
            TurfOwnerProfile.objects.update_or_create(
                user=request.user,
                defaults={
                    'owner_name': owner_name,
                    'business_name': business_name,
                    'contact_email': contact_email,
                    'city': city,
                    'address': address,
                    'zip_code': zip_code,
                }
            )

            # 4. Create the Turf Instance (Pending Approval)
            turf = Turf.objects.create(
                owner=request.user,
                name=business_name,
                description=description,
                address=address,
                city=city,
                price_per_hour=price_per_hour,
                latitude=latitude,
                longitude=longitude,
                map_share_url=map_share_url,
                is_active=False # Visible only after admin approves the owner
            )
            
            # 5. Set Sports
            if sport_ids:
                turf.sports.set(sport_ids)

            # 6. Handle Image Uploads (NO VIDEO in application form)
            # Videos can be added post-approval in the owner dashboard
            images = request.FILES.getlist('images')
            for i, image in enumerate(images):
                TurfImage.objects.create(
                    turf=turf,
                    image=image,
                    is_cover=(i == 0) # First image as cover
                )
        
        messages.success(request, "Application submitted successfully! Our team will review your details and contact you within 24-48 hours.")
        return redirect('users:dashboard')
    
    sports = SportType.objects.all()
    return render(request, 'users/register_owner.html', {'sports': sports})
