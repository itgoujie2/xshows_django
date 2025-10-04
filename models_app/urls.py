from django.urls import path
from . import views
from . import views_subscription

app_name = 'models_app'

urlpatterns = [
    # Model detail and related
    path('chat/<str:unique_username>/', views.ModelDetailView.as_view(), name='detail'),
    path('<int:id>/related/', views.RelatedModelsView.as_view(), name='ajax_related'),

    # Gender filtering
    path('gender/<str:sex>/', views.GenderFilterView.as_view(), name='sex_page'),

    # Favourites
    path('favorites/', views.FavouritesView.as_view(), name='favorites'),
    path('favourites/<int:id>/', views.ToggleFavouriteView.as_view(), name='attach_favourite'),

    # Subscriptions (Nudity Alerts)
    path('subscribe/<int:model_id>/', views_subscription.subscribe_toggle, name='subscribe_toggle'),
    path('subscriptions/', views_subscription.my_subscriptions, name='my_subscriptions'),
    path('unsubscribe/<int:subscription_id>/', views_subscription.unsubscribe, name='unsubscribe'),
    path('subscription-status/<int:model_id>/', views_subscription.subscription_status, name='subscription_status'),
]
