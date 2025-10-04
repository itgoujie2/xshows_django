"""
Celery tasks for scraping and updating webcam model data from various platforms.
Converted from Laravel Jobs with full implementation.
"""
from celery import shared_task
import logging
from django.utils import timezone
from django.db import transaction

from .models import WebcamModel
from .services import (
    ChaturbateService, StripcashService,
    XLoveCashService, BongaCashService,
    get_scraping_service
)
from core.models import Config

logger = logging.getLogger(__name__)


# Chaturbate Tasks
@shared_task
def get_data_from_chaturbate(limit=100):
    """Fetch initial data from Chaturbate platform"""
    logger.info(f"Fetching {limit} models from Chaturbate")

    try:
        config = Config.objects.filter(
            is_active=True,
            api_url__icontains='chaturbate'
        ).first()

        if not config:
            logger.warning("No active Chaturbate config found")
            return

        service = ChaturbateService()
        data = service.get_data(config, {'limit': limit})

        if data:
            service.save_data(data, config)
            logger.info(f"Successfully fetched Chaturbate data: {len(data)} models")
        else:
            logger.warning("No data received from Chaturbate")

    except Exception as e:
        logger.error(f"Error fetching Chaturbate data: {str(e)}", exc_info=True)


@shared_task
def update_chaturbate_data(limit=100):
    """Update existing Chaturbate model data"""
    logger.info("Updating Chaturbate data")

    try:
        config = Config.objects.filter(
            is_active=True,
            api_url__icontains='chaturbate'
        ).first()

        if not config:
            return

        service = ChaturbateService()
        data = service.get_data(config, {'limit': limit})

        if data:
            # Handle nested response
            models_list = data.get('results', []) if isinstance(data, dict) else data

            # Extract model IDs for online status update
            model_ids = [item.get('username') for item in models_list if item.get('username')]

            # Update models
            service.save_data(data, config)

            # Update online/offline status
            service.update_online_status(model_ids, Config.SOURCE_CHATURBATE)

            logger.info(f"Updated Chaturbate: {len(models_list)} models")

    except Exception as e:
        logger.error(f"Error updating Chaturbate data: {str(e)}", exc_info=True)


@shared_task
def update_chaturbate_categories():
    """Update categories for Chaturbate models"""
    logger.info("Updating Chaturbate categories")

    try:
        config = Config.objects.filter(
            is_active=True,
            api_url__icontains='chaturbate'
        ).first()

        if not config:
            return

        service = ChaturbateService()
        data = service.get_data(config, {'limit': 100})

        if data:
            service.update_categories(data, config)
            logger.info("Updated Chaturbate categories")

    except Exception as e:
        logger.error(f"Error updating Chaturbate categories: {str(e)}", exc_info=True)


# Stripcash Tasks
@shared_task
def get_data_from_stripcash(limit=100):
    """Fetch initial data from Stripcash platform"""
    logger.info(f"Fetching {limit} models from Stripcash")

    try:
        config = Config.objects.filter(
            is_active=True,
            api_url__icontains='stripcash'
        ).first()

        if not config:
            logger.warning("No active Stripcash config found")
            return

        service = StripcashService()
        data = service.get_data(config, {'limit': limit})

        if data and 'models' in data:
            service.save_data(data, config)
            logger.info(f"Successfully fetched Stripcash data: {len(data.get('models', []))} models")

    except Exception as e:
        logger.error(f"Error fetching Stripcash data: {str(e)}", exc_info=True)


@shared_task
def update_stripcash_data(limit=100):
    """Update existing Stripcash model data"""
    logger.info("Updating Stripcash data")

    try:
        config = Config.objects.filter(
            is_active=True,
            api_url__icontains='stripcash'
        ).first()

        if not config:
            return

        service = StripcashService()
        data = service.get_data(config, {'limit': limit})

        if data and 'models' in data:
            models_data = data.get('models', [])
            model_ids = [str(item.get('id')) for item in models_data if item.get('id')]

            service.save_data(data, config)
            service.update_online_status(model_ids, Config.SOURCE_STRIPCASH)

            logger.info(f"Updated Stripcash: {len(models_data)} models")

    except Exception as e:
        logger.error(f"Error updating Stripcash data: {str(e)}", exc_info=True)


@shared_task
def update_stripcash_categories():
    """Update categories for Stripcash models"""
    logger.info("Updating Stripcash categories")

    try:
        config = Config.objects.filter(
            is_active=True,
            api_url__icontains='stripcash'
        ).first()

        if not config:
            return

        service = StripcashService()
        data = service.get_data(config)

        if data:
            service.update_categories(data, config)
            logger.info("Updated Stripcash categories")

    except Exception as e:
        logger.error(f"Error updating Stripcash categories: {str(e)}", exc_info=True)


# XLoveCash Tasks
@shared_task
def get_data_from_xlovecash(limit=100):
    """Fetch initial data from XLoveCash platform"""
    logger.info(f"Fetching {limit} models from XLoveCash")

    try:
        config = Config.objects.filter(
            is_active=True,
            api_url__icontains='xlovecam'
        ).first()

        if not config:
            logger.warning("No active XLoveCash config found")
            return

        service = XLoveCashService()
        data = service.get_data(config, {'limit': limit})

        if data and 'content' in data:
            service.save_data(data, config)
            models_count = len(data.get('content', {}).get('models_list', []))
            logger.info(f"Successfully fetched XLoveCash data: {models_count} models")

    except Exception as e:
        logger.error(f"Error fetching XLoveCash data: {str(e)}", exc_info=True)


@shared_task
def update_xlovecash_data(limit=100):
    """Update existing XLoveCash model data"""
    logger.info("Updating XLoveCash data")

    try:
        config = Config.objects.filter(
            is_active=True,
            api_url__icontains='xlovecam'
        ).first()

        if not config:
            return

        service = XLoveCashService()
        data = service.get_data(config, {'limit': limit})

        if data and 'content' in data:
            models_list = data.get('content', {}).get('models_list', [])
            model_ids = [str(item.get('model_id')) for item in models_list if item.get('model_id')]

            service.save_data(data, config)
            service.update_online_status(model_ids, Config.SOURCE_XLOVECASH)

            logger.info(f"Updated XLoveCash: {len(models_list)} models")

    except Exception as e:
        logger.error(f"Error updating XLoveCash data: {str(e)}", exc_info=True)


@shared_task
def update_xlovecash_categories():
    """Update categories for XLoveCash models"""
    logger.info("Updating XLoveCash categories")

    try:
        config = Config.objects.filter(
            is_active=True,
            api_url__icontains='xlovecam'
        ).first()

        if not config:
            return

        service = XLoveCashService()
        data = service.get_data(config)

        if data:
            service.update_categories(data, config)
            logger.info("Updated XLoveCash categories")

    except Exception as e:
        logger.error(f"Error updating XLoveCash categories: {str(e)}", exc_info=True)


# BongaCash Tasks
@shared_task
def get_data_from_bongacash(limit=100):
    """Fetch initial data from BongaCash platform"""
    logger.info(f"Fetching {limit} models from BongaCash")

    try:
        config = Config.objects.filter(
            is_active=True,
            api_url__icontains='bonga'
        ).first()

        if not config:
            logger.warning("No active BongaCash config found")
            return

        service = BongaCashService()
        data = service.get_data(config, {'limit': limit})

        if data:
            service.save_data(data, config)
            logger.info(f"Successfully fetched BongaCash data: {len(data)} models")

    except Exception as e:
        logger.error(f"Error fetching BongaCash data: {str(e)}", exc_info=True)


@shared_task
def update_bongacash_data(limit=100):
    """Update existing BongaCash model data"""
    logger.info("Updating BongaCash data")

    try:
        config = Config.objects.filter(
            is_active=True,
            api_url__icontains='bonga'
        ).first()

        if not config:
            return

        service = BongaCashService()
        data = service.get_data(config, {'limit': limit})

        if data:
            model_ids = [item.get('username') for item in data if item.get('username')]

            service.save_data(data, config)
            service.update_online_status(model_ids, Config.SOURCE_BONGACASH)

            logger.info(f"Updated BongaCash: {len(data)} models")

    except Exception as e:
        logger.error(f"Error updating BongaCash data: {str(e)}", exc_info=True)


@shared_task
def update_bongacash_categories():
    """Update categories for BongaCash models"""
    logger.info("Updating BongaCash categories")

    try:
        config = Config.objects.filter(
            is_active=True,
            api_url__icontains='bonga'
        ).first()

        if not config:
            return

        service = BongaCashService()
        data = service.get_data(config)

        if data:
            service.update_categories(data, config)
            logger.info("Updated BongaCash categories")

    except Exception as e:
        logger.error(f"Error updating BongaCash categories: {str(e)}", exc_info=True)


# General Tasks
@shared_task
def update_online_status():
    """
    DEPRECATED: Do not use this task in scheduled jobs.
    Online status is now updated by individual scraping tasks.
    This task is kept for manual cleanup only.
    """
    logger.warning("update_online_status called - this should not run automatically")
    logger.info("Updating online status for all models based on last update time")

    try:
        # Mark models as offline if not updated in last 30 minutes
        threshold = timezone.now() - timezone.timedelta(minutes=30)
        offline_count = WebcamModel.objects.filter(
            updated_at__lt=threshold,
            is_online=True
        ).update(is_online=False)

        logger.info(f"Marked {offline_count} models as offline")

    except Exception as e:
        logger.error(f"Error updating online status: {str(e)}", exc_info=True)


@shared_task
def scrape_all_platforms(limit=100):
    """Scrape all active platforms at once"""
    logger.info("Scraping all platforms")

    update_chaturbate_data.delay(limit)
    update_stripcash_data.delay(limit)
    update_xlovecash_data.delay(limit)
    update_bongacash_data.delay(limit)


# Nudity Detection & Notification Tasks

@shared_task
def check_subscribed_models_for_nudity():
    """Check nudity for models with active subscriptions (memory-optimized for t3.small)"""
    from .models import Subscription, WebcamModel
    from django.conf import settings

    try:
        # Get unique model IDs with active subscriptions
        subscribed_model_ids = Subscription.objects.filter(
            is_active=True
        ).values_list('model_id', flat=True).distinct()

        # Get online models that are subscribed
        models = WebcamModel.objects.filter(
            id__in=subscribed_model_ids,
            is_online=True
        )

        total_count = models.count()

        # Memory optimization: Limit batch size for t3.small
        # Max 20 checks per run to prevent memory exhaustion
        max_checks = int(getattr(settings, 'MAX_NUDITY_CHECKS_PER_RUN', 20))

        if total_count > max_checks:
            # Prioritize models that haven't been checked recently
            models = models.order_by('nudity_last_check')[:max_checks]
            logger.info(f"Limited nudity checks to {max_checks} out of {total_count} subscribed models")
        else:
            logger.info(f"Checking nudity for {total_count} subscribed models")

        # Queue individual checks (they will run sequentially due to CELERY_WORKER_CONCURRENCY=2)
        for model in models:
            check_model_nudity.delay(model.id)

    except Exception as e:
        logger.error(f"Error in check_subscribed_models_for_nudity: {e}", exc_info=True)


@shared_task
def check_model_nudity(model_id):
    """Check if a specific model is showing nudity"""
    from .models import WebcamModel
    from .nudity_detector import NudityDetectionService

    try:
        model = WebcamModel.objects.get(id=model_id)

        # Skip if no image
        if not model.image:
            logger.warning(f"Model {model.display_name} has no image URL")
            return

        # Skip if image hasn't changed (check hash)
        detector = NudityDetectionService()

        # Check nudity
        is_naked, confidence, image_hash = detector.check_model_image(model.image)

        # Skip if same image as before (no change)
        if image_hash and model.nudity_image_hash == image_hash:
            logger.debug(f"Model {model.display_name} image unchanged, skipping")
            return

        # Update model
        model.is_naked = is_naked
        model.nudity_confidence = confidence
        model.nudity_last_check = timezone.now()
        model.nudity_image_hash = image_hash
        model.save(update_fields=[
            'is_naked', 'nudity_confidence', 'nudity_last_check', 'nudity_image_hash'
        ])

        confidence_str = f"{confidence:.2f}" if confidence is not None else "N/A"
        logger.info(
            f"Model {model.display_name}: is_naked={is_naked}, "
            f"confidence={confidence_str}"
        )

        # If naked, notify subscribers
        if is_naked:
            notify_subscribers.delay(model.id)

    except WebcamModel.DoesNotExist:
        logger.error(f"Model {model_id} not found")
    except Exception as e:
        logger.error(f"Error checking model {model_id} nudity: {e}", exc_info=True)


@shared_task
def notify_subscribers(model_id):
    """Send notifications to all subscribers of a model"""
    from .models import WebcamModel, Subscription, Notification
    from django.db.models import Q

    try:
        model = WebcamModel.objects.get(id=model_id)

        # Get subscriptions that need notification
        # Don't notify if already notified in last 30 minutes
        threshold = timezone.now() - timezone.timedelta(minutes=30)

        subscriptions = Subscription.objects.filter(
            model=model,
            is_active=True
        ).filter(
            Q(last_notified_at__isnull=True) |
            Q(last_notified_at__lt=threshold)
        )

        count = subscriptions.count()
        logger.info(f"Notifying {count} subscribers for {model.display_name}")

        for sub in subscriptions:
            # Create notification record
            notification = Notification.objects.create(
                subscription=sub,
                model=model,
                notification_type=Notification.TYPE_EMAIL,
                status=Notification.STATUS_PENDING
            )

            # Send email
            if sub.notification_method in ['email', 'both']:
                send_email_notification.delay(notification.id)

            # Update last notified time
            sub.last_notified_at = timezone.now()
            sub.save(update_fields=['last_notified_at'])

    except WebcamModel.DoesNotExist:
        logger.error(f"Model {model_id} not found")
    except Exception as e:
        logger.error(f"Error notifying subscribers for model {model_id}: {e}", exc_info=True)


@shared_task
def send_email_notification(notification_id):
    """Send email notification to user"""
    from .models import Notification
    from django.core.mail import send_mail
    from django.conf import settings

    try:
        notification = Notification.objects.get(id=notification_id)
        sub = notification.subscription
        model = notification.model

        # Get viewer count from JSON data
        viewers = 'N/A'
        if model.json_data and isinstance(model.json_data, dict):
            viewers = model.json_data.get('num_users', 'N/A')

        # Email subject
        subject = f'🔥 {model.display_name} is live and naked!'

        # Plain text message
        plain_message = f"""
Hi {sub.user.username},

Your favorite model {model.display_name} is currently live and showing nudity!

🔥 Watch now: {model.chat_url or 'https://chaturbate.com'}
👥 Viewers: {viewers}
📊 Nudity Confidence: {model.nudity_confidence * 100:.0f}%
⏰ Detected: {timezone.now().strftime('%Y-%m-%d %H:%M')}

Don't miss out!

---
To unsubscribe from {model.display_name}, visit: {settings.SITE_URL}/subscriptions/

XShows - Live Webcam Notifications
        """.strip()

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[sub.user.email],
            fail_silently=False,
        )

        # Update notification status
        notification.status = Notification.STATUS_SENT
        notification.sent_at = timezone.now()
        notification.save(update_fields=['status', 'sent_at'])

        logger.info(f"✅ Email sent to {sub.user.email} for model {model.display_name}")

    except Notification.DoesNotExist:
        logger.error(f"Notification {notification_id} not found")
    except Exception as e:
        # Mark as failed
        try:
            notification = Notification.objects.get(id=notification_id)
            notification.status = Notification.STATUS_FAILED
            notification.error_message = str(e)
            notification.save(update_fields=['status', 'error_message'])
        except:
            pass

        logger.error(f"❌ Error sending email for notification {notification_id}: {e}", exc_info=True)


@shared_task
def cleanup_old_nudity_cache():
    """Clean up old cached images (privacy)"""
    from .nudity_detector import NudityDetectionService

    try:
        detector = NudityDetectionService()
        removed_count = detector.cleanup_old_cache(max_age_hours=1)
        logger.info(f"Cache cleanup: removed {removed_count} old images")
        return removed_count
    except Exception as e:
        logger.error(f"Error in cache cleanup: {e}", exc_info=True)
        return 0


# Twitter Bot Tasks

@shared_task
def update_popular_models(min_viewers=500):
    """Update popular model flags based on viewer count"""
    from .twitter_bot import TwitterBot

    try:
        bot = TwitterBot()
        bot.update_popular_models(threshold=min_viewers)
        logger.info(f"Updated popular models (threshold: {min_viewers} viewers)")
    except Exception as e:
        logger.error(f"Error updating popular models: {e}", exc_info=True)


@shared_task
def tweet_popular_naked_models():
    """Tweet about popular models that are naked"""
    from .models import WebcamModel
    from .twitter_bot import TwitterBot
    from datetime import timedelta

    try:
        bot = TwitterBot()

        if not bot.enabled:
            logger.warning("Twitter bot is disabled - skipping tweets")
            return

        # Check daily tweet limit (max 10 tweets per day)
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        tweets_today = WebcamModel.objects.filter(
            last_tweeted_at__gte=today_start
        ).count()

        if tweets_today >= 10:
            logger.info(f"Daily tweet limit reached: {tweets_today}/10 tweets today")
            return

        # Calculate remaining tweets for today
        remaining_tweets = 10 - tweets_today

        # Get popular naked models
        models = WebcamModel.objects.filter(
            is_naked=True,
            is_online=True,
            is_popular=True
        ).order_by('-nudity_confidence')

        tweeted_count = 0
        max_tweets_this_run = min(1, remaining_tweets)  # Max 1 tweet per run

        for model in models:
            if bot.should_tweet_about_model(model):
                success = bot.post_tweet(model)
                if success:
                    tweeted_count += 1

                # Limit to 1 tweet per run (ensures max 12 per day with 2-hour schedule)
                if tweeted_count >= max_tweets_this_run:
                    break

        logger.info(f"Twitter bot: Posted {tweeted_count} tweets ({tweets_today + tweeted_count}/10 today)")

    except Exception as e:
        logger.error(f"Error in Twitter bot task: {e}", exc_info=True)
