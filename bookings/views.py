from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Booking
from turfs.models import Turf
from payments.models import DemoPayment
import datetime
import uuid

@login_required
def book_slot(request, turf_id):
    turf = get_object_or_404(Turf, id=turf_id)
    date_str = request.GET.get('date')
    
    if not date_str:
        return redirect('turfs:detail', turf_id=turf.id)
        
    booking_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    
    # Generate slots 6 AM to 11 PM
    slots = []
    for h in range(6, 23):
        start_time = datetime.time(h, 0)
        end_time = datetime.time(h+1, 0)
        
        # Check availability
        is_booked = Booking.objects.filter(
            turf=turf, 
            booking_date=booking_date, 
            start_time=start_time,
            status__in=['CONFIRMED', 'PENDING']
        ).exists()
        
        slots.append({
            'start': start_time,
            'end': end_time,
            'is_booked': is_booked
        })

    if request.method == 'POST':
        selected_time_str = request.POST.get('start_time')
        # Validate format HH:MM:SS or HH:MM
        # Simplification for demo
        h = int(selected_time_str.split(':')[0])
        start_time = datetime.time(h, 0)
        end_time = datetime.time(h+1, 0)
        
        # Create Pending Booking
        booking = Booking.objects.create(
            user=request.user,
            turf=turf,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            total_amount=turf.price_per_hour,
            status='PENDING'
        )
        return redirect('bookings:payment', booking_id=booking.booking_id)

    context = {
        'turf': turf,
        'date': booking_date,
        'slots': slots
    }
    return render(request, 'bookings/slot_selection.html', context)

@login_required
def payment_view(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    
    if request.method == 'POST':
        # Simulate Success
        status = request.POST.get('status')
        if status == 'SUCCESS':
            # Create Payment Record
            DemoPayment.objects.create(
                booking=booking,
                transaction_id=f"txn_{uuid.uuid4().hex[:10]}",
                amount=booking.total_amount,
                status='SUCCESS',
                gateway_response={'msg': 'Demo Success'}
            )
            booking.status = 'CONFIRMED'
            booking.payment_status = 'SUCCESS'
            booking.save()
            return redirect('bookings:success', booking_id=booking.booking_id)
        else:
            booking.payment_status = 'FAILED'
            booking.save()
            messages.error(request, "Payment Failed (Demo). Try again.")
    
    return render(request, 'bookings/payment.html', {'booking': booking})

@login_required
def booking_success(request, booking_id):
    booking = get_object_or_404(Booking, booking_id=booking_id, user=request.user)
    return render(request, 'bookings/success.html', {'booking': booking})
