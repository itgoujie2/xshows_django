"""
Scraping services for fetching model data from various platforms.
Converted from Laravel RequestApiService.
"""
import requests
import logging
from typing import Dict, List, Optional
from django.db import transaction
from django.db.models import Q

from .models import WebcamModel, ModelCategory
from categories.models import Category
from core.models import Config

logger = logging.getLogger(__name__)


class ScrapingService:
    """Base scraping service for all platforms"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def get_data(self, config: Config, params: Dict = None) -> Optional[Dict]:
        """Fetch data from API"""
        try:
            # Merge config data with params
            config_data = {}
            if config.data:
                import json
                try:
                    config_data = json.loads(config.data)
                except:
                    pass

            if params:
                config_data.update(params)

            # Add client_ip for Chaturbate
            if 'chaturbate' in config.api_url.lower() and 'client_ip' not in config_data:
                try:
                    ip_response = self.session.get('https://api.ipify.org', timeout=5)
                    config_data['client_ip'] = ip_response.text
                except:
                    config_data['client_ip'] = '8.8.8.8'

            # Make request based on method
            if config.method == 'GET':
                response = self.session.get(config.api_url, params=config_data, timeout=30)
            else:
                response = self.session.post(config.api_url, data=config_data, timeout=30)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"API request failed: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error fetching data: {str(e)}")
            return None

    def save_data(self, data: List[Dict], config: Config):
        """Save model data to database"""
        if not data:
            return

        # Handle nested response format (e.g., Chaturbate returns {"results": [...], "count": N})
        if isinstance(data, dict) and 'results' in data:
            data = data['results']

        # Parse data based on source
        parsed_models = self.parse_data(data, config)
        if not parsed_models:
            return

        model_ids = list(parsed_models.keys())

        with transaction.atomic():
            # Get existing models
            existing_models = WebcamModel.objects.filter(
                source=config.SOURCE_CHATURBATE if hasattr(config, 'SOURCE_CHATURBATE') else config.method,
                model_id__in=model_ids
            )

            existing_ids = set()
            # Update existing models
            for model in existing_models:
                model_data = parsed_models[model.model_id].copy()
                # Don't update unique_user_name and source for existing models
                model_data.pop('unique_user_name', None)
                model_data.pop('source', None)

                for key, value in model_data.items():
                    setattr(model, key, value)
                model.save()
                existing_ids.add(model.model_id)

            # Create new models
            new_models = []
            for model_id, model_data in parsed_models.items():
                if model_id not in existing_ids:
                    new_models.append(WebcamModel(**model_data))

            if new_models:
                WebcamModel.objects.bulk_create(new_models, ignore_conflicts=True)

            # Handle duplicate usernames
            self.handle_duplicate_usernames()

            logger.info(f"Saved {len(parsed_models)} models from {config.api_url}")

    def parse_data(self, data: List[Dict], config: Config) -> Dict:
        """Parse API data - to be overridden by platform-specific services"""
        raise NotImplementedError("Subclasses must implement parse_data")

    def update_online_status(self, model_ids: List[str], source: str):
        """Update online/offline status for models"""
        # Set online for models in the list
        WebcamModel.objects.filter(
            source=source,
            model_id__in=model_ids
        ).update(is_online=True)

        # Set offline for models not in the list
        WebcamModel.objects.filter(
            source=source
        ).exclude(
            model_id__in=model_ids
        ).update(is_online=False)

    def update_categories(self, data: List[Dict], config: Config):
        """Update categories/tags for models"""
        tags_map = self.extract_tags(data, config)
        if not tags_map:
            return

        model_ids = list(tags_map.keys())
        models = WebcamModel.objects.filter(
            source=config.method,
            model_id__in=model_ids
        ).prefetch_related('categories')

        for model in models:
            tags = tags_map.get(model.model_id, [])
            if tags:
                # Find matching categories
                categories = Category.objects.filter(
                    Q(name__in=tags) | Q(display_name__in=tags)
                )
                model.categories.set(categories)

    def extract_tags(self, data: List[Dict], config: Config) -> Dict[str, List[str]]:
        """Extract tags from data - to be overridden"""
        return {}

    def handle_duplicate_usernames(self):
        """Handle duplicate unique_user_name by appending numbers"""
        # Find duplicates
        from django.db.models import Count
        duplicates = WebcamModel.objects.values('unique_user_name').annotate(
            count=Count('id')
        ).filter(count__gt=1)

        for dup in duplicates:
            username = dup['unique_user_name']
            models = WebcamModel.objects.filter(unique_user_name=username).order_by('id')

            for idx, model in enumerate(models):
                if idx > 0:  # Keep first one as is
                    model.unique_user_name = f"{username}_{idx}"
                    model.save()


class ChaturbateService(ScrapingService):
    """Chaturbate scraping service"""

    def parse_data(self, data: List[Dict], config: Config) -> Dict:
        """Parse Chaturbate API response"""
        results = {}

        for item in data:
            username = item.get('username')
            if not username:
                continue

            results[username] = {
                'model_id': username,
                'user_name': username,
                'unique_user_name': username,
                'display_name': item.get('display_name') or username,
                'age': item.get('age'),
                'gender': item.get('gender'),
                'description': item.get('room_subject', ''),
                'image': item.get('image_url', ''),
                'iframe': item.get('iframe_embed'),
                'link_embed': None,
                'link_snapshot': item.get('image_url'),
                'chat_url': item.get('chat_room_url', ''),
                'is_online': True,
                'source': Config.SOURCE_CHATURBATE,
                'json_data': item,
            }

        return results

    def extract_tags(self, data: List[Dict], config: Config) -> Dict[str, List[str]]:
        """Extract tags from Chaturbate data"""
        tags_map = {}
        for item in data:
            username = item.get('username')
            tags = item.get('tags', [])
            if username and tags:
                tags_map[username] = tags
        return tags_map


class StripcashService(ScrapingService):
    """Stripcash scraping service"""

    def parse_data(self, data: Dict, config: Config) -> Dict:
        """Parse Stripcash API response"""
        results = {}
        models_data = data.get('models', [])

        # Get userId from config
        import json
        config_data = {}
        try:
            config_data = json.loads(config.data) if config.data else {}
        except:
            pass

        user_id = config_data.get('userId', '')

        for item in models_data:
            model_id = item.get('id')
            username = item.get('username')
            if not model_id:
                continue

            link_embed = f"https://lite-iframe.stripcdn.com/{username}?userId={user_id}"
            chat_url = f"https://go.gldrdr.com/?userId={user_id}&path=/cams/{username}"
            iframe_url = f"https://go.schjmpl.com/?userId={user_id}&refreshRate=60&hasPlayer=true&hasLive=true&hasName=true&path={username}"

            results[model_id] = {
                'model_id': str(model_id),
                'user_name': username,
                'unique_user_name': username,
                'display_name': username,
                'age': None,
                'gender': item.get('gender'),
                'description': None,
                'image': item.get('previewUrl', ''),
                'iframe': iframe_url,
                'link_embed': link_embed,
                'link_snapshot': item.get('snapshotUrl'),
                'chat_url': chat_url,
                'is_online': True,
                'source': Config.SOURCE_STRIPCASH,
                'json_data': item,
            }

        return results

    def extract_tags(self, data: Dict, config: Config) -> Dict[str, List[str]]:
        """Extract tags from Stripcash data"""
        tags_map = {}
        models_data = data.get('models', [])
        for item in models_data:
            username = item.get('username')
            tags = item.get('tags', [])
            if username and tags:
                tags_map[username] = tags
        return tags_map


class XLoveCashService(ScrapingService):
    """XLoveCash scraping service"""

    def parse_data(self, data: Dict, config: Config) -> Dict:
        """Parse XLoveCash API response"""
        results = {}
        models_list = data.get('content', {}).get('models_list', [])

        for item in models_list:
            model_id = item.get('model_id')
            if not model_id:
                continue

            image_url = item.get('model_profil_photo', '')
            if image_url.startswith('http://'):
                image_url = 'https://' + image_url.replace('http://', '')

            results[model_id] = {
                'model_id': str(model_id),
                'user_name': item.get('nick', ''),
                'unique_user_name': item.get('nick', ''),
                'display_name': item.get('nick', ''),
                'age': None,  # Will be updated in second pass
                'gender': None,  # Will be updated in second pass
                'description': None,  # Will be updated in second pass
                'image': image_url,
                'iframe': None,
                'link_embed': None,
                'link_snapshot': item.get('camLive'),
                'chat_url': item.get('model_link', ''),
                'is_online': bool(item.get('online')),
                'source': Config.SOURCE_XLOVECASH,
                'json_data': item,
            }

        # Second pass: Get detailed profile info
        if results:
            self._update_xlovecash_profiles(results, config)

        return results

    def _update_xlovecash_profiles(self, results: Dict, config: Config):
        """Get detailed profile information for XLoveCash models"""
        model_ids = list(results.keys())
        chunk_size = 100

        # Process in chunks
        for i in range(0, len(model_ids), chunk_size):
            chunk = model_ids[i:i + chunk_size]

            # Create temporary config for profile endpoint
            profile_config = Config(
                method='POST',
                api_url='https://webservice-affiliate.xlovecam.com/model/getprofileinfo/',
                data=config.data
            )

            profile_data = self.get_data(profile_config, {'modelid': chunk})
            if profile_data and 'content' in profile_data:
                for model_id, info in profile_data['content'].items():
                    if model_id in results:
                        model_info = info.get('model', {})
                        info_by_lang = info.get('infoByLang', {})

                        results[model_id].update({
                            'age': model_info.get('age'),
                            'gender': model_info.get('sex'),
                            'description': info_by_lang.get('description', ''),
                        })

    def extract_tags(self, data: Dict, config: Config) -> Dict[str, List[str]]:
        """Extract tags from XLoveCash data"""
        tags_map = {}
        models_list = data.get('content', {}).get('models_list', [])
        for item in models_list:
            model_id = item.get('model_id')
            tags = item.get('tagList', [])
            if model_id and tags:
                tags_map[str(model_id)] = tags
        return tags_map


class BongaCashService(ScrapingService):
    """BongaCash scraping service"""

    def parse_data(self, data: List[Dict], config: Config) -> Dict:
        """Parse BongaCash API response"""
        results = {}

        # Get config data for chat URL
        import json
        config_data = {}
        try:
            config_data = json.loads(config.data) if config.data else {}
        except:
            pass

        c_param = config_data.get('c', '')
        chat_url_template = f"https://bngpt.com/promo.php?type=direct_link&v=2&c={c_param}&amute=1&models[]=%s&model_offline=profile"

        for item in data:
            username = item.get('username')
            if not username:
                continue

            profile_image = item.get('profile_images', {}).get('profile_image', '')
            if profile_image and not profile_image.startswith('https://'):
                profile_image = 'https://' + profile_image.replace('//', '')

            results[username] = {
                'model_id': username,
                'user_name': username,
                'unique_user_name': username,
                'display_name': item.get('display_name', username),
                'age': item.get('display_age'),
                'gender': item.get('gender'),
                'description': item.get('turns_on', ''),
                'image': profile_image,
                'iframe': None,
                'link_embed': item.get('embed_chat_url'),
                'link_snapshot': item.get('profile_images', {}).get('thumbnail_image_big_live'),
                'chat_url': chat_url_template % username,
                'is_online': True,
                'source': Config.SOURCE_BONGACASH,
                'json_data': item,
            }

        return results

    def extract_tags(self, data: List[Dict], config: Config) -> Dict[str, List[str]]:
        """Extract tags from BongaCash data"""
        tags_map = {}
        for item in data:
            username = item.get('username')
            tags = item.get('tags', [])
            if username and tags:
                tags_map[username] = tags
        return tags_map


# Service factory
def get_scraping_service(source: str) -> ScrapingService:
    """Get appropriate scraping service based on source"""
    services = {
        Config.SOURCE_CHATURBATE: ChaturbateService,
        Config.SOURCE_STRIPCASH: StripcashService,
        Config.SOURCE_XLOVECASH: XLoveCashService,
        Config.SOURCE_BONGACASH: BongaCashService,
    }

    service_class = services.get(source)
    if service_class:
        return service_class()
    else:
        return ScrapingService()
