from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.admin_site import admin_site  # Import custom admin site

# Trigger registration by importing admin modules
import users.admin
import turfs.admin
import bookings.admin

urlpatterns = [
    path('admin/', admin_site.urls), # Use custom site
    path('api/v1/', include('turf_platform.api_urls')), # REST APIs
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('turfs/', include('turfs.urls')),
    path('bookings/', include('bookings.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
