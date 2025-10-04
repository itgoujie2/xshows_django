import os
from celery import Celery
from celery.schedules import crontab

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xshows.settings')

app = Celery('xshows')

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
app.config_from_object('django.conf:settings', namespace='CELERY')

# Load task modules from all registered Django apps.
app.autodiscover_tasks()


# Celery Beat Schedule (periodic tasks)
app.conf.beat_schedule = {
    # Scrape all platforms every 5 minutes (includes online status update)
    'scrape-all-platforms': {
        'task': 'models_app.tasks.scrape_all_platforms',
        'schedule': crontab(minute='*/5'),
        'args': (100,),  # Limit per platform
    },

    # Check nudity for subscribed models every 5 minutes
    'check-nudity-for-subscriptions': {
        'task': 'models_app.tasks.check_subscribed_models_for_nudity',
        'schedule': crontab(minute='*/5'),
    },

    # Cleanup old cached images every hour (privacy)
    'cleanup-nudity-cache': {
        'task': 'models_app.tasks.cleanup_old_nudity_cache',
        'schedule': crontab(minute=0),  # Every hour
    },

    # Update popular models every 10 minutes
    'update-popular-models': {
        'task': 'models_app.tasks.update_popular_models',
        'schedule': crontab(minute='*/10'),
        'args': (500,),  # Minimum 500 viewers to be popular
    },

    # Tweet about popular naked models every 2 hours (max 12 per day)
    'tweet-popular-naked-models': {
        'task': 'models_app.tasks.tweet_popular_naked_models',
        'schedule': crontab(minute=0, hour='*/2'),  # Every 2 hours
    },
}


@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
