from django.urls import path, re_path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('robots.txt', views.robots_txt, name='robots'),
    # Category pattern - exclude specific paths like sitemap.xml
    re_path(r'^(?!sitemap\.xml$)(?P<category>[\w-]+)/$', views.HomeView.as_view(), name='home_category'),
]
