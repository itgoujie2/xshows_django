from django.db import models
from django.conf import settings
from categories.models import Category


class WebcamModel(models.Model):
    """Webcam model representing performers from different streaming platforms"""

    model_id = models.CharField(max_length=50)
    user_name = models.CharField(max_length=50)
    unique_user_name = models.CharField(max_length=100, unique=True, blank=True, null=True)
    display_name = models.CharField(max_length=255)
    is_online = models.BooleanField(default=True)
    age = models.IntegerField(null=True, blank=True)
    gender = models.CharField(max_length=40, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    image = models.CharField(max_length=255)
    iframe = models.TextField(null=True, blank=True)
    link_embed = models.TextField(null=True, blank=True)
    link_snapshot = models.TextField(null=True, blank=True)
    url_stream = models.TextField(null=True, blank=True)
    chat_url = models.TextField(null=True, blank=True)
    source = models.CharField(max_length=12)
    json_data = models.JSONField()

    # Nudity detection fields
    is_naked = models.BooleanField(default=False)
    nudity_confidence = models.FloatField(null=True, blank=True)
    nudity_last_check = models.DateTimeField(null=True, blank=True)
    nudity_image_hash = models.CharField(max_length=64, null=True, blank=True)

    # Twitter bot tracking
    is_popular = models.BooleanField(default=False)
    last_tweeted_at = models.DateTimeField(null=True, blank=True)
    tweet_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Many-to-many relationships
    categories = models.ManyToManyField(Category, through='ModelCategory', related_name='models')
    favourited_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='Favourite',
        related_name='favourited_models'
    )

    class Meta:
        db_table = 'models'
        indexes = [
            models.Index(fields=['model_id']),
            models.Index(fields=['user_name']),
            models.Index(fields=['gender']),
            models.Index(fields=['source']),
            models.Index(fields=['is_naked']),
        ]

    def __str__(self):
        return self.display_name or self.user_name


class ModelCategory(models.Model):
    """Through model for Model-Category many-to-many relationship"""

    model = models.ForeignKey(WebcamModel, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'model_category'
        unique_together = ['model', 'category']


class Favourite(models.Model):
    """User favourites for webcam models"""

    model = models.ForeignKey(WebcamModel, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'favourites'
        unique_together = ['model', 'user']


class XLoveCashTag(models.Model):
    """Tags from XLoveCash platform"""

    tag = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'xlovecash_tags'

    def __str__(self):
        return self.tag


class Subscription(models.Model):
    """User subscription to a specific webcam model for nudity notifications"""

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
    """Notification record for tracking sent nudity alerts"""

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
