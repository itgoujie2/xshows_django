"""
Context processors to make variables available to all templates.
Similar to Laravel's view composers.
"""
from django.conf import settings
from categories.models import Category


def site_settings(request):
    """Add global site settings to template context"""
    return {
        'site_title': 'XShows',
        'logo_path': settings.LOGO_PATH,
        'meta_description': 'Live webcam models from multiple platforms',
        'meta_keywords': 'webcam, live chat, models',
    }


def categories_processor(request):
    """Make categories available globally"""
    return {
        'categories': Category.objects.filter(is_active=True).order_by('display_name')
    }
