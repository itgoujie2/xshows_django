"""
Views for subscription management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.contrib import messages
from .models import WebcamModel, Subscription, Notification


@login_required
@require_POST
def subscribe_toggle(request, model_id):
    """
    AJAX endpoint to subscribe/unsubscribe from a model
    """
    model = get_object_or_404(WebcamModel, id=model_id)

    # Check if subscription exists
    subscription = Subscription.objects.filter(
        user=request.user,
        model=model
    ).first()

    if subscription:
        # Toggle subscription
        subscription.is_active = not subscription.is_active
        subscription.save()
        is_subscribed = subscription.is_active
        action = 'subscribed' if is_subscribed else 'unsubscribed'
    else:
        # Create new subscription
        subscription = Subscription.objects.create(
            user=request.user,
            model=model,
            is_active=True,
            notification_method='email'
        )
        is_subscribed = True
        action = 'subscribed'

    return JsonResponse({
        'success': True,
        'is_subscribed': is_subscribed,
        'action': action,
        'message': f'You are now {action} to {model.display_name}'
    })


@login_required
def my_subscriptions(request):
    """
    Show user's subscriptions page
    """
    subscriptions = Subscription.objects.filter(
        user=request.user,
        is_active=True
    ).select_related('model').order_by('-created_at')

    # Get notification history for user
    notifications = Notification.objects.filter(
        subscription__user=request.user
    ).select_related('model', 'subscription').order_by('-created_at')[:20]

    context = {
        'subscriptions': subscriptions,
        'notifications': notifications,
    }

    return render(request, 'models_app/my_subscriptions.html', context)


@login_required
@require_POST
def unsubscribe(request, subscription_id):
    """
    Unsubscribe from a model
    """
    subscription = get_object_or_404(
        Subscription,
        id=subscription_id,
        user=request.user
    )

    model_name = subscription.model.display_name
    subscription.is_active = False
    subscription.save()

    messages.success(request, f'Unsubscribed from {model_name}')

    # Redirect back to subscriptions page or model page
    return redirect('models_app:my_subscriptions')


@login_required
def subscription_status(request, model_id):
    """
    Check if user is subscribed to a model (for AJAX)
    """
    is_subscribed = Subscription.objects.filter(
        user=request.user,
        model_id=model_id,
        is_active=True
    ).exists()

    return JsonResponse({
        'is_subscribed': is_subscribed
    })
