"""
Quick test script to scrape Chaturbate without Config setup
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xshows.settings')
django.setup()

import requests
from models_app.models import WebcamModel
from categories.models import Category
from django.db import transaction

# Chaturbate public API endpoint
# According to docs, you need a webmaster account username (wm parameter)
# You can sign up for free at: https://chaturbate.com/accounts/register/
API_URL = "https://chaturbate.com/api/public/affiliates/onlinerooms/"

WM_USERNAME = "xvfw7"

print(f"Fetching online models from Chaturbate (wm={WM_USERNAME})...")

# Get public IP
try:
    ip_response = requests.get('https://api.ipify.org', timeout=5)
    client_ip = ip_response.text
    print(f"Using client IP: {client_ip}")
except:
    client_ip = '8.8.8.8'  # Fallback
    print(f"Using fallback IP: {client_ip}")

params = {
    'wm': WM_USERNAME,
    'limit': 20,
    'client_ip': client_ip
}
response = requests.get(API_URL, params=params, timeout=30)

if response.status_code == 200:
    import json
    data = response.json()

    print(f"\n✓ API Response type: {type(data)}")
    print(f"✓ Raw response (first 500 chars):\n{json.dumps(data, indent=2)[:500]}")

    # Check if data is a list or dict
    if isinstance(data, dict):
        print(f"✓ Response keys: {list(data.keys())}")
        # Try different possible keys
        if 'results' in data:
            models_list = data['results']
        elif 'models' in data:
            models_list = data['models']
        elif 'data' in data:
            models_list = data['data']
        else:
            # Maybe the dict itself contains model data
            models_list = [data] if 'username' in data else []
    elif isinstance(data, list):
        models_list = data
    else:
        models_list = []

    print(f"✓ Found {len(models_list)} online models")

    models_to_create = []

    for item in models_list:
        username = item.get('username')
        if not username:
            continue

        print(f"  - {username}: {item.get('num_users', 0)} viewers")

        # Prepare model data
        model_data = {
            'model_id': username,
            'user_name': username,
            'display_name': item.get('display_name') or username,
            'age': item.get('age'),
            'gender': item.get('gender', 'female'),
            'description': ' '.join(item.get('tags', [])) if item.get('tags') else '',
            'image': item.get('image_url') or '',
            'is_online': True,
            'source': 'chaturbate',
            'chat_url': f"https://chaturbate.com/{username}/",
            'iframe': item.get('iframe_embed_revshare', ''),
            'link_embed': item.get('iframe_embed_revshare', ''),
            'link_snapshot': item.get('chat_room_url_revshare', ''),
            'url_stream': item.get('chat_room_url_revshare', ''),
            'json_data': item
        }

        # Create or update
        model, created = WebcamModel.objects.update_or_create(
            model_id=username,
            source='chaturbate',
            defaults=model_data
        )

        print(f"    {'Created' if created else 'Updated'}: {model.display_name}")

    print(f"\n✓ Successfully scraped {len(data)} models from Chaturbate")
    print(f"Total Chaturbate models in DB: {WebcamModel.objects.filter(source='chaturbate').count()}")
    print(f"Online models: {WebcamModel.objects.filter(is_online=True).count()}")
else:
    print(f"✗ Error: HTTP {response.status_code}")
    print(response.text)
