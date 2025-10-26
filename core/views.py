from django.shortcuts import render
from django.views.generic import ListView
from django.conf import settings
from django.http import HttpResponse
from django.template import loader
from models_app.models import WebcamModel
from categories.models import Category


class HomeView(ListView):
    """
    Home view displaying webcam models.
    Converted from HomeController@index in Laravel.
    """
    model = WebcamModel
    template_name = 'core/index.html'
    context_object_name = 'models'
    paginate_by = 20

    def get_queryset(self):
        queryset = WebcamModel.objects.filter(is_online=True)

        # Filter by category if provided
        category = self.kwargs.get('category')
        if category:
            queryset = queryset.filter(categories__name=category)

        return queryset.select_related().prefetch_related('categories')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.filter(is_active=True)
        context['site_title'] = 'NakedAlerts'
        context['logo_path'] = settings.LOGO_PATH
        context['meta_description'] = 'Get instant alerts when webcam models go live. AI-powered notifications for your favorite creators. Free webcam stream alerts - never miss a show.'
        context['meta_keywords'] = 'webcam model alerts, webcam alerts, cam girl notifications, live cam alerts, webcam stream notifications, adult webcam alerts'

        # Add current category if applicable
        category_name = self.kwargs.get('category')
        if category_name:
            try:
                context['current_category'] = Category.objects.get(name=category_name)
            except Category.DoesNotExist:
                pass

        return context


def robots_txt(request):
    """
    Serve robots.txt file with dynamic sitemap URL
    """
    template = loader.get_template('robots.txt')
    context = {
        'site_url': settings.SITE_URL
    }
    return HttpResponse(template.render(context), content_type='text/plain')
