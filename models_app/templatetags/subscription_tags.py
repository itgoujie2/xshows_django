"""
Template tags for subscription functionality
"""
from django import template
from models_app.models import Subscription

register = template.Library()


@register.simple_tag(takes_context=True)
def is_subscribed(context, model):
    """
    Check if the current user is subscribed to a model
    Usage: {% is_subscribed model as subscribed %}
    """
    request = context.get('request')
    if not request or not request.user.is_authenticated:
        return False

    return Subscription.objects.filter(
        user=request.user,
        model=model,
        is_active=True
    ).exists()


@register.filter
def user_subscribed_to(model, user):
    """
    Check if a user is subscribed to a model
    Usage: {{ model|user_subscribed_to:request.user }}
    """
    if not user or not user.is_authenticated:
        return False

    return Subscription.objects.filter(
        user=user,
        model=model,
        is_active=True
    ).exists()
