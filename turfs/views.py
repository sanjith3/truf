from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Turf, TurfImage
from .forms import TurfForm, TurfImageForm

def turf_list(request):
    turfs = Turf.objects.filter(is_active=True)
    city = request.GET.get('city')
    if city:
        turfs = turfs.filter(city__icontains=city)
        
    context = {
        'turfs': turfs
    }
    return render(request, 'turfs/turf_list.html', context)

def turf_detail(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    context = {
        'turf': turf
    }
    return render(request, 'turfs/turf_detail.html', context)

@login_required
def add_turf(request):
    # Ensure user is an approved owner
    if not request.user.is_turf_owner or not request.user.is_owner_approved:
        messages.error(request, "Only approved owners can add turfs.")
        return redirect('users:dashboard')

    if request.method == 'POST':
        form = TurfForm(request.POST)
        if form.is_valid():
            turf = form.save(commit=False)
            turf.owner = request.user
            turf.is_active = False # Requires admin approval for new turfs too usually, or auto-approve if owner is trusted
            turf.save()
            form.save_m2m() # Save sports
            messages.success(request, f"Turf '{turf.name}' added successfully! It will be visible after review.")
            return redirect('users:dashboard')
    else:
        form = TurfForm()
    
    return render(request, 'turfs/add_edit_turf.html', {'form': form, 'title': 'Add New Turf'})

@login_required
def edit_turf(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id, owner=request.user)
    
    if request.method == 'POST':
        form = TurfForm(request.POST, instance=turf)
        if form.is_valid():
            form.save()
            messages.success(request, f"Turf '{turf.name}' updated successfully!")
            return redirect('users:dashboard')
    else:
        form = TurfForm(instance=turf)
    
    return render(request, 'turfs/add_edit_turf.html', {'form': form, 'title': f'Edit {turf.name}', 'turf': turf})

@login_required
def manage_turf_images(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id, owner=request.user)
    
    if request.method == 'POST':
        form = TurfImageForm(request.POST, request.FILES)
        if form.is_valid():
            img = TurfImage(
                turf=turf,
                image=form.cleaned_data['image'],
                is_cover=form.cleaned_data['is_cover']
            )
            # If this is cover, unset others
            if img.is_cover:
                turf.images.filter(is_cover=True).update(is_cover=False)
            img.save()
            messages.success(request, "Image uploaded successfully!")
            return redirect('turfs:manage_images', turf_id=turf.id)
    else:
        form = TurfImageForm()
    
    images = turf.images.all()
    return render(request, 'turfs/manage_images.html', {'turf': turf, 'images': images, 'form': form})
