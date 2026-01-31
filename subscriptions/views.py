from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import SubscriptionPlan, OwnerSubscription
from django.utils import timezone

@login_required
def plan_list(request):
    if not request.user.is_turf_owner:
        messages.error(request, "Only turf owners can access subscription plans.")
        return redirect('core:home')
    
    plans = SubscriptionPlan.objects.filter(is_active=True).order_by('tier')
    try:
        current_subscription = request.user.subscription
    except OwnerSubscription.DoesNotExist:
        current_subscription = None
        
    context = {
        'plans': plans,
        'current_subscription': current_subscription,
        'now': timezone.now()
    }
    return render(request, 'subscriptions/plan_list.html', context)

@login_required
def subscribe(request, plan_id):
    if not request.user.is_turf_owner:
        return redirect('core:home')
        
    plan = get_object_or_404(SubscriptionPlan, id=plan_id, is_active=True)
    
    # In a real app, integrate payment gateway here.
    # For this demo, we auto-activate the plan.
    
    subscription, created = OwnerSubscription.objects.get_or_create(
        owner=request.user,
        defaults={'plan': plan, 'start_date': timezone.now()}
    )
    
    if not created:
        subscription.plan = plan
        subscription.start_date = timezone.now()
        subscription.status = 'ACTIVE'
        # Reset end_date so save() recalculates it
        subscription.end_date = None 
        subscription.save()
        
    messages.success(request, f"Successfully upgraded to {plan.name} plan!")
    return redirect('subscriptions:plan_list')
