"""
URL configuration for xshows project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),

    # Authentication URLs (allauth)
    path('accounts/', include('allauth.urls')),

    # Custom auth URLs (compatible with Laravel routes)
    path('', include('users.urls')),

    # Core app URLs
    path('', include('core.urls')),

    # Models app URLs
    path('', include('models_app.urls')),

    # Categories URLs
    path('', include('categories.urls')),

    # Admin panel URLs
    path('admin-panel/', include('admin_panel.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
