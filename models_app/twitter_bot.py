"""
Twitter bot service for posting nudity alerts
"""
import tweepy
import logging
from django.conf import settings
from django.utils import timezone
from .models import WebcamModel

logger = logging.getLogger(__name__)


class TwitterBot:
    """Twitter bot for posting model alerts"""

    def __init__(self):
        """Initialize Twitter API client"""
        try:
            # Try OAuth 2.0 first (Client ID/Secret)
            if hasattr(settings, 'TWITTER_CLIENT_ID') and settings.TWITTER_CLIENT_ID:
                # OAuth 2.0 Client Credentials
                self.client = tweepy.Client(
                    consumer_key=settings.TWITTER_API_KEY,
                    consumer_secret=settings.TWITTER_API_SECRET,
                    access_token=settings.TWITTER_ACCESS_TOKEN,
                    access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
                )
                logger.info("Twitter bot initialized with OAuth 1.0a")
            else:
                # Fallback to OAuth 1.0a
                self.client = tweepy.Client(
                    consumer_key=settings.TWITTER_API_KEY,
                    consumer_secret=settings.TWITTER_API_SECRET,
                    access_token=settings.TWITTER_ACCESS_TOKEN,
                    access_token_secret=settings.TWITTER_ACCESS_TOKEN_SECRET
                )
                logger.info("Twitter bot initialized with OAuth 1.0a")

            self.enabled = True
        except Exception as e:
            logger.error(f"Failed to initialize Twitter bot: {e}")
            self.enabled = False

    def create_tweet_text(self, model):
        """
        Create tweet text for a naked model alert

        Args:
            model: WebcamModel instance

        Returns:
            str: Tweet text
        """
        # Get viewer count from json_data
        viewers = 'N/A'
        if model.json_data and isinstance(model.json_data, dict):
            viewers = model.json_data.get('num_users', 'N/A')

        # Create engaging tweet
        emojis = ['🔥', '💋', '🌶️', '😈', '💦']
        confidence_pct = int(model.nudity_confidence * 100) if model.nudity_confidence else 0

        tweet = f"""🔴 LIVE & NAKED! {emojis[model.id % len(emojis)]}

{model.display_name} is showing off right NOW!

👥 {viewers} viewers watching
🔥 {confidence_pct}% confidence
📍 {model.source.upper()}

Watch: {model.chat_url or 'https://chaturbate.com'}

#Chaturbate #LiveCam #NSFW"""

        # Twitter max length is 280 characters
        if len(tweet) > 280:
            # Shorten if needed
            tweet = f"""🔴 {model.display_name} is LIVE & NAKED! 🔥

👥 {viewers} watching now
Watch: {model.chat_url or 'https://chaturbate.com'}

#Chaturbate #LiveCam"""

        return tweet

    def post_tweet(self, model):
        """
        Post a tweet about a naked model

        Args:
            model: WebcamModel instance

        Returns:
            bool: Success status
        """
        if not self.enabled:
            logger.warning("Twitter bot is disabled")
            return False

        try:
            tweet_text = self.create_tweet_text(model)

            # Post tweet using API v2
            response = self.client.create_tweet(text=tweet_text)

            # Update model tracking
            model.last_tweeted_at = timezone.now()
            model.tweet_count += 1
            model.save(update_fields=['last_tweeted_at', 'tweet_count'])

            logger.info(f"✅ Tweeted about {model.display_name} (ID: {response.data['id']})")
            return True

        except tweepy.TweepyException as e:
            logger.error(f"Twitter API error for {model.display_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Error posting tweet for {model.display_name}: {e}")
            return False

    def should_tweet_about_model(self, model):
        """
        Determine if we should tweet about this model

        Args:
            model: WebcamModel instance

        Returns:
            bool: Whether to tweet
        """
        # Must be naked and online
        if not model.is_naked or not model.is_online:
            return False

        # Must be popular (we'll set this based on viewer count)
        if not model.is_popular:
            return False

        # Rate limit: Don't tweet about same model more than once per hour
        if model.last_tweeted_at:
            time_since_last_tweet = timezone.now() - model.last_tweeted_at
            if time_since_last_tweet.total_seconds() < 3600:  # 1 hour
                return False

        return True

    def get_popular_models(self, limit=10):
        """
        Get popular models based on viewer count

        Args:
            limit: Max number of models to return

        Returns:
            QuerySet: Popular models
        """
        from django.db.models import F

        # Get online models sorted by viewer count
        models = WebcamModel.objects.filter(
            is_online=True
        ).extra(
            select={'viewer_count': "CAST(json_data->>'$.num_users' AS UNSIGNED)"}
        ).order_by('-viewer_count')[:limit]

        return models

    def update_popular_models(self, threshold=500):
        """
        Mark models as popular based on viewer count

        Args:
            threshold: Minimum viewer count to be considered popular
        """
        try:
            # Get all online models
            models = WebcamModel.objects.filter(is_online=True)

            updated_count = 0
            for model in models:
                if model.json_data and isinstance(model.json_data, dict):
                    viewers = model.json_data.get('num_users', 0)
                    try:
                        viewers = int(viewers)
                    except (ValueError, TypeError):
                        viewers = 0

                    # Mark as popular if above threshold
                    is_popular = viewers >= threshold
                    if model.is_popular != is_popular:
                        model.is_popular = is_popular
                        model.save(update_fields=['is_popular'])
                        updated_count += 1

            logger.info(f"Updated {updated_count} models' popularity status")

        except Exception as e:
            logger.error(f"Error updating popular models: {e}")
