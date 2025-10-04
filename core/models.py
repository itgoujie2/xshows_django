from django.db import models


class Config(models.Model):
    """Configuration model for API settings"""

    # Constants
    METHOD_CHOICES = [
        ('GET', 'query'),
        ('POST', 'form_params'),
    ]

    SOURCE_STRIPCASH = 'stripcash'
    SOURCE_XLOVECASH = 'xlovecash'
    SOURCE_CHATURBATE = 'chaturbate'
    SOURCE_BONGACASH = 'bongacash'

    # Gender mapping for different sources
    GENDER_MAPPING = {
        'trans': ['trans', 's', 'femaleTranny'],
        'male': ['men', 'male', 'm', 'M', 'Couple Female + Male', 'maleFemale'],
        'female': ['female', 'F', 'f', 'Couple Female + Female', 'Couple Female + Male',
                   'Female', 'females', 'femaleTranny', 'maleFemale']
    }

    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    api_url = models.TextField()
    data = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'config'

    def __str__(self):
        return f"{self.method} - {self.api_url[:50]}"


class Setting(models.Model):
    """Application settings model"""

    key = models.CharField(max_length=255, unique=True)
    value = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'settings'

    def __str__(self):
        return self.key
