from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from .models import CustomUser, TurfOwnerProfile

User = get_user_model()

# ... Login/OTP Views (unchanged) ...
def login_view(request):
    if request.method == 'POST':
        phone = request.POST.get('phone_number')
        if phone:
            user, created = User.objects.get_or_create(phone_number=phone)
            otp = user.generate_demo_otp()
            request.session['auth_user_id'] = user.id
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

@login_required
def register_as_owner(request):
    if request.method == 'POST':
        # 1. Collect Form Data
        business_name = request.POST.get('business_name')
        contact_email = request.POST.get('contact_email')
        city = request.POST.get('city')
        address = request.POST.get('address')
        zip_code = request.POST.get('zip_code')
        
        # 2. Update User Flags
        request.user.is_turf_owner = True
        request.user.is_owner_approved = False  
        request.user.owner_application_date = timezone.now()
        request.user.save()
        
        # 3. Create or Update Profile
        TurfOwnerProfile.objects.update_or_create(
            user=request.user,
            defaults={
                'business_name': business_name,
                'contact_email': contact_email,
                'city': city,
                'address': address,
                'zip_code': zip_code,
            }
        )
        
        messages.success(request, "Application submitted! Waiting for Admin verification.")
        return redirect('users:dashboard')
    
    return render(request, 'users/register_owner.html')
