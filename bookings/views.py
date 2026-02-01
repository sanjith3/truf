from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from .models import Booking
from turfs.models import Turf
from payments.models import DemoPayment
import datetime
import uuid

@login_required
@transaction.atomic
def book_slot(request, turf_id):
    from turfs.services import AvailabilityService
    turf = get_object_or_404(Turf, id=turf_id)
    date_str = request.GET.get('date')
    
    if not date_str:
        return redirect('turfs:detail', turf_id=turf.id)
        
    try:
        booking_date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return redirect('turfs:detail', turf_id=turf.id)
    
    # Get Enhanced Slots
    slots, is_date_avail, closed_reason = AvailabilityService.get_slots_for_date(turf, booking_date)

    if request.method == 'POST':
        if not is_date_avail:
            messages.error(request, f"Cannot book: {closed_reason}")
            return redirect('bookings:book', turf_id=turf.id)

        selected_time_str = request.POST.get('start_time')
        h = int(selected_time_str.split(':')[0])
        start_time = datetime.time(h, 0)
        end_time = datetime.time(h+1, 0)
        
        # Guard: Check if specific slot is enabled
        slot_data = next((s for s in slots if s['start'] == start_time), None)
        if not slot_data or not slot_data['is_enabled'] or slot_data['is_booked']:
            messages.error(request, "This slot is no longer available.")
            return redirect(f"{request.path}?date={date_str}")

        # CRITICAL: Race condition prevention with database lock
        # select_for_update() locks the rows until transaction commits
        existing_booking = Booking.objects.select_for_update().filter(
            turf=turf,
            booking_date=booking_date,
            start_time=start_time,
            status__in=['CONFIRMED', 'PENDING']
        ).exists()
        
        if existing_booking:
            messages.error(request, "Sorry! This slot was just booked by another user. Please select a different time.")
            return redirect(f"{request.path}?date={date_str}")

        # Create Pending Booking (Reserved for 10 minutes)
        # Price ALWAYS from server, never trust client input
        booking = Booking.objects.create(
            user=request.user,
            turf=turf,
            booking_date=booking_date,
            start_time=start_time,
            end_time=end_time,
            base_amount=turf.price_per_hour,  # Server-side only, prevents price manipulation
            status='PENDING',
            expires_at=timezone.now() + datetime.timedelta(minutes=10)
        )
        return redirect('bookings:payment', booking_id=booking.booking_id)

    context = {
        'turf': turf,
        'date': booking_date,
        'slots': slots,
        'is_date_avail': is_date_avail,
        'closed_reason': closed_reason
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
