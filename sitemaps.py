"""
Sitemaps configuration for nakedalerts.com
"""
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from models_app.models import WebcamModel
from categories.models import Category


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages"""
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['core:home']

    def location(self, item):
        return reverse(item)


class CategorySitemap(Sitemap):
    """Sitemap for category pages"""
    priority = 0.8
    changefreq = 'daily'

    def items(self):
        return Category.objects.filter(is_active=True).order_by('name')

    def location(self, obj):
        return reverse('core:home_category', args=[obj.name])

    def lastmod(self, obj):
        return obj.updated_at


class GenderSitemap(Sitemap):
    """Sitemap for gender filter pages"""
    priority = 0.7
    changefreq = 'daily'

    def items(self):
        return ['female', 'male', 'trans']

    def location(self, item):
        return reverse('models_app:sex_page', args=[item])


class ModelDetailSitemap(Sitemap):
    """Sitemap for individual webcam model pages"""
    priority = 0.6
    changefreq = 'hourly'
    limit = 5000  # Limit to prevent too large sitemaps

    def items(self):
        # Only include models that have a unique_user_name and are currently online or recently updated
        return WebcamModel.objects.filter(
            unique_user_name__isnull=False
        ).exclude(unique_user_name='').order_by('-updated_at')[:self.limit]

    def location(self, obj):
        return reverse('models_app:detail', args=[obj.unique_user_name])

    def lastmod(self, obj):
        return obj.updated_at


class OnlineModelsSitemap(Sitemap):
    """Sitemap for online webcam models (higher priority)"""
    priority = 0.9
    changefreq = 'always'  # These change very frequently
    limit = 1000

    def items(self):
        # Only currently online models with unique usernames
        return WebcamModel.objects.filter(
            is_online=True,
            unique_user_name__isnull=False
        ).exclude(unique_user_name='').order_by('-updated_at')[:self.limit]

    def location(self, obj):
        return reverse('models_app:detail', args=[obj.unique_user_name])

    def lastmod(self, obj):
        return obj.updated_at


class NakedModelsSitemap(Sitemap):
    """Sitemap for naked webcam models (high priority for the site's main feature)"""
    priority = 0.95
    changefreq = 'always'
    limit = 500

    def items(self):
        # Naked models that are currently online
        return WebcamModel.objects.filter(
            is_naked=True,
            is_online=True,
            unique_user_name__isnull=False
        ).exclude(unique_user_name='').order_by('-nudity_last_check')[:self.limit]

    def location(self, obj):
        return reverse('models_app:detail', args=[obj.unique_user_name])

    def lastmod(self, obj):
        return obj.nudity_last_check or obj.updated_at
