# Model Subscription with AI Nudity Detection - Implementation Plan

## Problem Confirmed
After analyzing the Chaturbate data:
- ❌ Only 36% of models have explicit nudity tags
- ❌ Tags are user-defined hashtags, not real-time status
- ❌ `current_show` field only shows "public/private/hidden", not nudity status
- ✅ **Solution: AI image detection required**

## Implementation Strategy

### Phase 1: Subscription System (2-3 hours)
1. Database migrations for subscriptions
2. Django models for Subscription & Notification
3. UI: Subscribe/Unsubscribe buttons
4. User subscription management page

### Phase 2: AI Nudity Detection with NudeNet (2-3 hours)
1. Install NudeNet library
2. Create nudity detection service
3. Image download & caching
4. Celery task for AI checking

### Phase 3: Notification System (2-3 hours)
1. Email notifications (SendGrid/Django SMTP)
2. Rate limiting (don't spam users)
3. Notification templates
4. Notification history

### Phase 4: Integration (1 hour)
1. Connect scraping → nudity check → notifications
2. Update Celery schedule
3. Testing

**Total Time: 8-10 hours**

---

## Step-by-Step Implementation

### STEP 1: Database Schema

```sql
-- Subscriptions
CREATE TABLE subscriptions (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    model_id INT NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    notification_method ENUM('email', 'sms', 'both') DEFAULT 'email',
    last_notified_at DATETIME NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_model (user_id, model_id)
);

CREATE INDEX idx_subscriptions_active ON subscriptions(is_active);
CREATE INDEX idx_subscriptions_user ON subscriptions(user_id);
CREATE INDEX idx_subscriptions_model ON subscriptions(model_id);

-- Notifications
CREATE TABLE notifications (
    id INT PRIMARY KEY AUTO_INCREMENT,
    subscription_id INT NOT NULL,
    model_id INT NOT NULL,
    notification_type ENUM('email', 'sms') DEFAULT 'email',
    status ENUM('pending', 'sent', 'failed') DEFAULT 'pending',
    sent_at DATETIME NULL,
    error_message TEXT NULL,
    created_at DATETIME NOT NULL,
    FOREIGN KEY (subscription_id) REFERENCES subscriptions(id) ON DELETE CASCADE,
    FOREIGN KEY (model_id) REFERENCES models(id) ON DELETE CASCADE
);

CREATE INDEX idx_notifications_status ON notifications(status);
CREATE INDEX idx_notifications_subscription ON notifications(subscription_id);

-- Add nudity tracking to models
ALTER TABLE models ADD COLUMN is_naked BOOLEAN DEFAULT FALSE;
ALTER TABLE models ADD COLUMN nudity_confidence FLOAT NULL;
ALTER TABLE models ADD COLUMN nudity_last_check DATETIME NULL;
ALTER TABLE models ADD COLUMN nudity_image_hash VARCHAR(64) NULL;

CREATE INDEX idx_models_naked ON models(is_naked);

-- Add phone to users (for SMS later)
ALTER TABLE users ADD COLUMN phone_number VARCHAR(20) NULL;
ALTER TABLE users ADD COLUMN notification_preferences JSON NULL;
```

### STEP 2: Django Models

```python
# models_app/models.py

class Subscription(models.Model):
    """User subscription to a specific model"""

    NOTIFICATION_EMAIL = 'email'
    NOTIFICATION_SMS = 'sms'
    NOTIFICATION_BOTH = 'both'

    NOTIFICATION_CHOICES = [
        (NOTIFICATION_EMAIL, 'Email'),
        (NOTIFICATION_SMS, 'SMS'),
        (NOTIFICATION_BOTH, 'Both'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    model = models.ForeignKey(WebcamModel, on_delete=models.CASCADE, related_name='subscribers')
    is_active = models.BooleanField(default=True)
    notification_method = models.CharField(max_length=10, choices=NOTIFICATION_CHOICES, default=NOTIFICATION_EMAIL)
    last_notified_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'subscriptions'
        unique_together = ['user', 'model']
        indexes = [
            models.Index(fields=['is_active']),
            models.Index(fields=['user']),
            models.Index(fields=['model']),
        ]

    def __str__(self):
        return f"{self.user.username} → {self.model.display_name}"


class Notification(models.Model):
    """Notification record for tracking sent notifications"""

    TYPE_EMAIL = 'email'
    TYPE_SMS = 'sms'

    TYPE_CHOICES = [
        (TYPE_EMAIL, 'Email'),
        (TYPE_SMS, 'SMS'),
    ]

    STATUS_PENDING = 'pending'
    STATUS_SENT = 'sent'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_SENT, 'Sent'),
        (STATUS_FAILED, 'Failed'),
    ]

    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name='notifications')
    model = models.ForeignKey(WebcamModel, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=10, choices=TYPE_CHOICES, default=TYPE_EMAIL)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['subscription']),
        ]

    def __str__(self):
        return f"{self.notification_type} to {self.subscription.user.username} - {self.status}"
```

### STEP 3: NudeNet Integration

```python
# models_app/nudity_detector.py

import os
import hashlib
import requests
from PIL import Image
from io import BytesIO
from nudenet import NudeDetector
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class NudityDetectionService:
    """Service for detecting nudity in images using NudeNet"""

    def __init__(self):
        self.detector = NudeDetector()
        self.cache_dir = os.path.join(settings.BASE_DIR, 'media', 'nudity_cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    def download_image(self, image_url):
        """Download image from URL"""
        try:
            response = requests.get(image_url, timeout=10)
            if response.status_code == 200:
                # Generate hash for caching
                image_hash = hashlib.md5(response.content).hexdigest()
                cache_path = os.path.join(self.cache_dir, f"{image_hash}.jpg")

                # Save to cache
                with open(cache_path, 'wb') as f:
                    f.write(response.content)

                return cache_path, image_hash
        except Exception as e:
            logger.error(f"Error downloading image {image_url}: {e}")
            return None, None

    def detect_nudity(self, image_path):
        """
        Detect nudity in image
        Returns: (is_naked: bool, confidence: float, details: dict)
        """
        try:
            predictions = self.detector.detect(image_path)

            # Nudity classes to check
            explicit_classes = [
                'FEMALE_BREAST_EXPOSED',
                'FEMALE_GENITALIA_EXPOSED',
                'MALE_GENITALIA_EXPOSED',
                'BUTTOCKS_EXPOSED',
                'ANUS_EXPOSED',
            ]

            # Check if any explicit parts detected with confidence > 0.6
            nudity_detections = [
                p for p in predictions
                if p['class'] in explicit_classes and p['score'] > 0.6
            ]

            if nudity_detections:
                # Get highest confidence
                max_confidence = max(d['score'] for d in nudity_detections)
                is_naked = True
            else:
                max_confidence = 0.0
                is_naked = False

            details = {
                'detections': len(nudity_detections),
                'classes_found': list(set(d['class'] for d in nudity_detections)),
                'all_predictions': predictions
            }

            logger.info(f"Nudity detection: is_naked={is_naked}, confidence={max_confidence:.2f}")

            return is_naked, max_confidence, details

        except Exception as e:
            logger.error(f"Error detecting nudity: {e}")
            return False, 0.0, {'error': str(e)}

    def check_model_image(self, image_url):
        """
        Complete workflow: download image, check nudity, cleanup
        Returns: (is_naked: bool, confidence: float, image_hash: str)
        """
        image_path, image_hash = self.download_image(image_url)

        if not image_path:
            return False, 0.0, None

        try:
            is_naked, confidence, details = self.detect_nudity(image_path)

            # Delete cached image after check (privacy)
            if os.path.exists(image_path):
                os.remove(image_path)

            return is_naked, confidence, image_hash

        except Exception as e:
            logger.error(f"Error in check_model_image: {e}")
            # Cleanup on error
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
            return False, 0.0, image_hash
```

### STEP 4: Celery Tasks

```python
# models_app/tasks.py (ADD THESE)

from .nudity_detector import NudityDetectionService

@shared_task
def check_subscribed_models_for_nudity():
    """Check nudity for models with active subscriptions"""
    from .models import Subscription, WebcamModel

    # Get unique model IDs with active subscriptions
    subscribed_model_ids = Subscription.objects.filter(
        is_active=True
    ).values_list('model_id', flat=True).distinct()

    # Get online models that are subscribed
    models = WebcamModel.objects.filter(
        id__in=subscribed_model_ids,
        is_online=True
    )

    logger.info(f"Checking nudity for {models.count()} subscribed models")

    # Queue individual checks
    for model in models:
        check_model_nudity.delay(model.id)


@shared_task
def check_model_nudity(model_id):
    """Check if a specific model is showing nudity"""
    from .models import WebcamModel

    try:
        model = WebcamModel.objects.get(id=model_id)

        # Skip if image hasn't changed (using hash)
        if not model.image:
            logger.warning(f"Model {model.display_name} has no image")
            return

        detector = NudityDetectionService()
        is_naked, confidence, image_hash = detector.check_model_image(model.image)

        # Update model
        model.is_naked = is_naked
        model.nudity_confidence = confidence
        model.nudity_last_check = timezone.now()
        model.nudity_image_hash = image_hash
        model.save(update_fields=['is_naked', 'nudity_confidence', 'nudity_last_check', 'nudity_image_hash'])

        logger.info(f"Model {model.display_name}: is_naked={is_naked}, confidence={confidence:.2f}")

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

        logger.info(f"Notifying {subscriptions.count()} subscribers for {model.display_name}")

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

    except Exception as e:
        logger.error(f"Error notifying subscribers for model {model_id}: {e}", exc_info=True)


@shared_task
def send_email_notification(notification_id):
    """Send email notification"""
    from .models import Notification
    from django.core.mail import send_mail
    from django.template.loader import render_to_string

    try:
        notification = Notification.objects.get(id=notification_id)
        sub = notification.subscription
        model = notification.model

        # Render email
        subject = f'🔥 {model.display_name} is live and naked!'

        html_message = render_to_string('emails/nudity_notification.html', {
            'user': sub.user,
            'model': model,
            'subscription': sub,
        })

        plain_message = f"""
Hi {sub.user.username},

Your favorite model {model.display_name} is live and showing nudity!

Watch now: {model.chat_url}

Viewers: {model.json_data.get('num_users', 'N/A') if model.json_data else 'N/A'}
Confidence: {model.nudity_confidence * 100:.0f}%

---
To unsubscribe, click here: {settings.SITE_URL}/subscriptions/unsubscribe/{sub.id}/

XShows
        """

        # Send email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[sub.user.email],
            html_message=html_message,
            fail_silently=False,
        )

        # Update notification status
        notification.status = Notification.STATUS_SENT
        notification.sent_at = timezone.now()
        notification.save()

        logger.info(f"Email sent to {sub.user.email} for model {model.display_name}")

    except Exception as e:
        # Mark as failed
        notification.status = Notification.STATUS_FAILED
        notification.error_message = str(e)
        notification.save()
        logger.error(f"Error sending email for notification {notification_id}: {e}", exc_info=True)
```

### STEP 5: Update Celery Schedule

```python
# xshows/celery.py

app.conf.beat_schedule = {
    # Scrape all platforms every 5 minutes
    'scrape-all-platforms': {
        'task': 'models_app.tasks.scrape_all_platforms',
        'schedule': crontab(minute='*/5'),
        'args': (100,),
    },

    # Check nudity for subscribed models every 5 minutes (after scraping)
    'check-nudity-for-subscriptions': {
        'task': 'models_app.tasks.check_subscribed_models_for_nudity',
        'schedule': crontab(minute='*/5'),
    },
}
```

---

## Testing Plan

1. **Test Subscription**:
   - Create user account
   - Subscribe to a model
   - Check database

2. **Test NudeNet**:
   - Download sample image
   - Run detection manually
   - Check accuracy

3. **Test Notification**:
   - Trigger notification manually
   - Check email received
   - Verify rate limiting

4. **Test Full Flow**:
   - Subscribe to model
   - Wait for scraping (5 min)
   - Check if nudity detected
   - Verify email received

---

## Cost Estimate (Monthly)

### For 1000 Users with avg 5 subscriptions each

**Scenario**: 5000 total subscriptions, checked every 5 minutes = 1,440,000 checks/month

| Item | Cost |
|------|------|
| **NudeNet** (runs locally) | $0 |
| **Image downloads** (bandwidth) | ~$5 |
| **Email (SendGrid Free)** | $0 (up to 100/day) |
| **Email (SendGrid Pro)** | $15 (40k emails/month) |
| **Server CPU/RAM** | +$10 (upgrade instance) |
| **Total** | **$15-30/month** |

Very affordable!

---

## Privacy & Legal

1. ✅ Images deleted immediately after check
2. ✅ Only store hash + is_naked boolean
3. ✅ Users must opt-in to subscribe
4. ✅ Easy unsubscribe
5. ✅ Age gate on signup
6. ✅ GDPR compliant (user consent)

---

Ready to start implementing? I'll begin with:
1. Database migrations
2. Django models
3. Install NudeNet
4. Create nudity detector service

Should I proceed?
