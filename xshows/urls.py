"""
URL configuration for xshows project.
"""
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from sitemaps import (
    StaticViewSitemap,
    CategorySitemap,
    GenderSitemap,
    ModelDetailSitemap,
    OnlineModelsSitemap,
    NakedModelsSitemap,
)

# Sitemap configuration
sitemaps = {
    'static': StaticViewSitemap,
    'categories': CategorySitemap,
    'genders': GenderSitemap,
    'models': ModelDetailSitemap,
    'online': OnlineModelsSitemap,
    'naked': NakedModelsSitemap,
}

urlpatterns = [
    # Sitemap - exact match, no trailing slash allowed
    re_path(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),

    # Admin URLs
    path('admin/', admin.site.urls),

    # Authentication URLs (allauth)
    path('accounts/', include('allauth.urls')),

    # Admin panel URLs
    path('admin-panel/', include('admin_panel.urls')),

    # Custom auth URLs (compatible with Laravel routes)
    path('', include('users.urls')),

    # Models app URLs
    path('', include('models_app.urls')),

    # Categories URLs
    path('', include('categories.urls')),

    # Core app URLs - Must be last due to catch-all category pattern
    path('', include('core.urls')),
]

# Serve static and media files in development
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
