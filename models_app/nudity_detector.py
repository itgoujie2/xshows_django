"""
Nudity Detection Service using NudeNet AI
Detects nudity in webcam model images for subscription notifications
"""
import os
import hashlib
import requests
import logging
from django.conf import settings
from nudenet import NudeDetector

logger = logging.getLogger(__name__)


class NudityDetectionService:
    """Service for detecting nudity in images using NudeNet AI"""

    # Class-level detector (shared across instances for memory efficiency)
    _detector = None
    _detector_loaded = False

    def __init__(self):
        """Initialize the service (lazy load detector only when needed)"""
        # Create cache directory for temporary image storage
        self.cache_dir = os.path.join(settings.BASE_DIR, 'media', 'nudity_cache')
        os.makedirs(self.cache_dir, exist_ok=True)

    @classmethod
    def _get_detector(cls):
        """Lazy load NudeNet detector (only once, shared across all instances)"""
        if not cls._detector_loaded:
            try:
                logger.info("Loading NudeNet model (this may take a moment)...")
                cls._detector = NudeDetector()
                cls._detector_loaded = True
                logger.info("NudeNet detector loaded successfully")
            except Exception as e:
                logger.error(f"Error loading NudeNet: {e}")
                cls._detector = None
                cls._detector_loaded = True  # Don't retry every time
        return cls._detector

    @property
    def detector(self):
        """Get the shared detector instance"""
        return self._get_detector()

    def download_image(self, image_url):
        """
        Download image from URL and save to cache
        Returns: (cache_path, image_hash) or (None, None) on error
        """
        try:
            # Download image
            response = requests.get(image_url, timeout=10, headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            })

            if response.status_code != 200:
                logger.error(f"Failed to download image: HTTP {response.status_code}")
                return None, None

            # Generate hash for caching and duplicate detection
            image_hash = hashlib.md5(response.content).hexdigest()
            cache_path = os.path.join(self.cache_dir, f"{image_hash}.jpg")

            # Save to cache
            with open(cache_path, 'wb') as f:
                f.write(response.content)

            logger.info(f"Image downloaded successfully: {image_hash}")
            return cache_path, image_hash

        except requests.RequestException as e:
            logger.error(f"Error downloading image {image_url}: {e}")
            return None, None
        except Exception as e:
            logger.error(f"Unexpected error downloading image: {e}")
            return None, None

    def detect_nudity(self, image_path):
        """
        Detect nudity in image using NudeNet
        Returns: (is_naked: bool, confidence: float, details: dict)
        """
        if not self.detector:
            logger.error("NudeNet detector not initialized")
            return False, 0.0, {'error': 'Detector not initialized'}

        try:
            # Run detection
            predictions = self.detector.detect(image_path)

            # Classes that indicate explicit nudity
            explicit_classes = [
                'FEMALE_BREAST_EXPOSED',
                'FEMALE_GENITALIA_EXPOSED',
                'MALE_GENITALIA_EXPOSED',
                'BUTTOCKS_EXPOSED',
                'ANUS_EXPOSED',
            ]

            # Filter predictions for explicit nudity (confidence > 0.6)
            nudity_detections = [
                p for p in predictions
                if p['class'] in explicit_classes and p['score'] > 0.6
            ]

            if nudity_detections:
                # Get highest confidence score
                max_confidence = max(d['score'] for d in nudity_detections)
                is_naked = True
                classes_found = list(set(d['class'] for d in nudity_detections))
            else:
                max_confidence = 0.0
                is_naked = False
                classes_found = []

            details = {
                'detections_count': len(nudity_detections),
                'classes_found': classes_found,
                'total_predictions': len(predictions),
            }

            logger.info(
                f"Nudity detection complete: is_naked={is_naked}, "
                f"confidence={max_confidence:.2f}, classes={classes_found}"
            )

            return is_naked, max_confidence, details

        except Exception as e:
            logger.error(f"Error detecting nudity in {image_path}: {e}", exc_info=True)
            return False, 0.0, {'error': str(e)}

    def check_model_image(self, image_url):
        """
        Complete workflow: download image, check nudity, cleanup
        Returns: (is_naked: bool, confidence: float, image_hash: str)
        """
        # Download image
        image_path, image_hash = self.download_image(image_url)

        if not image_path:
            logger.warning(f"Failed to download image from {image_url}")
            return False, 0.0, None

        try:
            # Detect nudity
            is_naked, confidence, details = self.detect_nudity(image_path)

            logger.info(
                f"Image check complete: is_naked={is_naked}, confidence={confidence:.2f}, "
                f"hash={image_hash}, details={details}"
            )

            return is_naked, confidence, image_hash

        except Exception as e:
            logger.error(f"Error in check_model_image: {e}", exc_info=True)
            return False, 0.0, image_hash

        finally:
            # Always cleanup image file (privacy & disk space)
            try:
                if image_path and os.path.exists(image_path):
                    os.remove(image_path)
                    logger.debug(f"Cleaned up image: {image_path}")
            except Exception as e:
                logger.warning(f"Failed to delete cached image {image_path}: {e}")

    def cleanup_old_cache(self, max_age_hours=1):
        """
        Remove cached images older than max_age_hours
        Should be called periodically via Celery task
        """
        import time
        removed_count = 0

        try:
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600

            for filename in os.listdir(self.cache_dir):
                file_path = os.path.join(self.cache_dir, filename)

                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)

                    if file_age > max_age_seconds:
                        os.remove(file_path)
                        removed_count += 1

            if removed_count > 0:
                logger.info(f"Cleaned up {removed_count} old cached images")

        except Exception as e:
            logger.error(f"Error cleaning up cache: {e}")

        return removed_count
