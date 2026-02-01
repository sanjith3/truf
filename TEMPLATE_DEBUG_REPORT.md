# Template Rendering Debug Report

## 1. URL Pattern
**File:** `core/urls.py`
```python
path('platform-admin/review-application/<int:user_id>/', views.review_owner_application, name='review_application')
```

## 2. Django View Function
**File:** `core/views.py`
```python
@user_passes_test(lambda u: u.is_staff)
def review_owner_application(request, user_id):
    """Detailed view of turf owner application for review"""
    owner = get_object_or_404(
        CustomUser.objects.select_related('owner_profile').prefetch_related(
            'turfs', 'turfs__images', 'turfs__sports', 'turfs__videos'
        ),
        id=user_id,
        is_turf_owner=True,
        is_owner_approved=False
    )
    
    formatted_date = owner.owner_application_date.strftime("%b %d, %Y") if owner.owner_application_date else "N/A"
    
    context = {
        'owner': owner,
        'turf': owner.turfs.first(),
        'title': f'Review Application - {owner.owner_profile.business_name}',
        'formatted_date': formatted_date,
    }
    
    return render(request, 'platform_admin/partner_application_review.html', context)
```

## 3. Exact Template Path
`platform_admin/partner_application_review.html`
Resolved to absolute path: `d:\truff-booking-system\templates\platform_admin\partner_application_review.html`

## 4. TEMPLATES Setting
**File:** `turf_platform/settings.py`
```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'], # Points to d:\truff-booking-system\templates
        'APP_DIRS': True,
        # ... options
    },
]
```

## 5. HttpResponse Verification
The view uses `django.shortcuts.render()`, which properly passes the request and context to the `DjangoTemplates` backend. It does **NOT** use `HttpResponse()` with raw strings or `render_to_string()` manually.

## Root Cause Fix
The literal rendering of `{{ ... }}` was caused by invalid split-line template tags (e.g., `{{ owner... \n ...name }}`) in the original file. These have been consolidated to single lines, and the file location has been standardized to `platform_admin/`.
