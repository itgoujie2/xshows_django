# Scraping Implementation Guide

## ✅ What's Been Implemented

The scraping functionality has been fully implemented! Here's what you have:

### Services Created (`models_app/services.py`):
- ✅ **ScrapingService** - Base service with common functionality
- ✅ **ChaturbateService** - Chaturbate API scraper
- ✅ **StripcashService** - Stripcash API scraper
- ✅ **XLoveCashService** - XLoveCash API scraper (with 2-pass profile fetching)
- ✅ **BongaCashService** - BongaCash API scraper

### Features Implemented:
- ✅ Data fetching from APIs
- ✅ Model data parsing and normalization
- ✅ Bulk create/update operations
- ✅ Online/offline status tracking
- ✅ Category/tag assignment
- ✅ Duplicate username handling
- ✅ Error handling and logging

### Celery Tasks (`models_app/tasks.py`):
- ✅ 13 fully implemented tasks (not stubs anymore!)
- ✅ Platform-specific scrapers
- ✅ Category update tasks
- ✅ Online status monitoring
- ✅ Scheduled execution ready

## 🚀 How to Use

### Step 1: Set Up API Configs

First, you need to add API configurations for the platforms you want to scrape.

Via Django Admin (http://localhost:8000/admin/core/config/):

**Example: Chaturbate**
```
Method: GET
API URL: https://chaturbate.com/api/public/affiliates/onlinerooms/
Data: {"wm": "your_webmaster_code"}
Is Active: ✓
```

**Example: Stripcash**
```
Method: GET
API URL: https://stripcash.com/api/models/
Data: {"userId": "your_user_id"}
Is Active: ✓
```

**Example: XLoveCash**
```
Method: POST
API URL: https://webservice-affiliate.xlovecam.com/model/getmodelsonline/
Data: {"affiliate_id": "your_affiliate_id"}
Is Active: ✓
```

**Example: BongaCash**
```
Method: GET
API URL: https://bongacams.com/tools/listing_v2.php
Data: {"c": "your_campaign_code"}
Is Active: ✓
```

### Step 2: Test Scraping Manually

Use the management command to test:

```bash
cd ~/Downloads/xshows_django
source venv/bin/activate

# Scrape from Chaturbate
python manage.py scrape_models chaturbate --limit 50

# Scrape from Stripcash
python manage.py scrape_models stripcash --limit 50

# Scrape from all platforms
python manage.py scrape_models all --limit 100
```

### Step 3: Set Up Celery Workers

To run scraping in the background:

#### Terminal 1: Start Redis (if not running)
```bash
redis-server
```

#### Terminal 2: Start Celery Worker
```bash
cd ~/Downloads/xshows_django
source venv/bin/activate
celery -A xshows worker -l info
```

#### Terminal 3: Start Celery Beat (scheduler)
```bash
cd ~/Downloads/xshows_django
source venv/bin/activate
celery -A xshows beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Step 4: Trigger Tasks Manually

From Django shell:
```bash
python manage.py shell
```

```python
from models_app.tasks import *

# Scrape Chaturbate
update_chaturbate_data.delay(100)

# Scrape all platforms
scrape_all_platforms.delay(50)

# Update online status
update_online_status.delay()
```

## 📋 Available Tasks

### Data Fetching Tasks:
- `get_data_from_chaturbate(limit)` - Initial fetch
- `get_data_from_stripcash(limit)` - Initial fetch
- `get_data_from_xlovecash(limit)` - Initial fetch
- `get_data_from_bongacash(limit)` - Initial fetch

### Update Tasks (use these for regular updates):
- `update_chaturbate_data(limit)` - Update existing data
- `update_stripcash_data(limit)` - Update existing data
- `update_xlovecash_data(limit)` - Update existing data
- `update_bongacash_data(limit)` - Update existing data

### Category Tasks:
- `update_chaturbate_categories()` - Update tags/categories
- `update_stripcash_categories()` - Update tags/categories
- `update_xlovecash_categories()` - Update tags/categories
- `update_bongacash_categories()` - Update tags/categories

### Utility Tasks:
- `update_online_status()` - Mark old models offline
- `scrape_all_platforms(limit)` - Scrape all at once

## 🔄 Scheduled Tasks

The tasks are already configured in `xshows/celery.py` to run automatically:

- **Every 30 minutes**: Update data from all platforms
- **Every 5 minutes**: Update online/offline status

## 🧪 Testing Without Real APIs

If you don't have API credentials yet, you can test with mock data:

```python
# In Django shell
from models_app.models import WebcamModel
from core.models import Config

# Create fake models to test the views
WebcamModel.objects.create(
    model_id='test123',
    user_name='test_model',
    display_name='Test Model',
    age=25,
    gender='female',
    description='Test description',
    image='https://via.placeholder.com/300x400/FF69B4/FFF?text=Test',
    is_online=True,
    source='chaturbate',
    chat_url='https://chaturbate.com/',
    json_data={}
)
```

## 🔍 Monitoring & Debugging

### Check Logs:
```bash
# In Celery worker terminal, you'll see:
# [INFO] Fetching 100 models from Chaturbate
# [INFO] Successfully fetched Chaturbate data: 100 models
# [INFO] Updated Chaturbate: 100 models
```

### Check Database:
```bash
python manage.py shell
```

```python
from models_app.models import WebcamModel

# Count models by source
WebcamModel.objects.filter(source='chaturbate').count()
WebcamModel.objects.filter(source='stripcash').count()

# Check online models
WebcamModel.objects.filter(is_online=True).count()

# Get latest models
WebcamModel.objects.order_by('-created_at')[:10]
```

### Django Admin:
Visit http://localhost:8000/admin/models_app/webcammodel/ to see scraped models

## ⚙️ Configuration Notes

### API Requirements:

**Chaturbate:**
- Requires webmaster account
- API docs: https://chaturbate.com/affiliates/api/

**Stripcash:**
- Requires affiliate account
- Get userId from affiliate dashboard

**XLoveCash:**
- Requires affiliate ID
- Two-pass system: first gets model list, second gets profiles

**BongaCash:**
- Requires campaign code
- Get from affiliate tools

### Rate Limiting:
The services have built-in timeout (30s) and use a session for connection pooling. You may want to add:
- Retry logic
- Exponential backoff
- Rate limiting

## 🚨 Troubleshooting

### "No active config found"
- Make sure you've created Config entries in Django Admin
- Check that `is_active` is checked
- Verify the API URL contains the platform name

### Models not appearing on site:
- Check `is_online=True`
- Verify models have valid `user_name` and `display_name`
- Check logs for parsing errors

### Celery not running tasks:
- Make sure Redis is running: `redis-cli ping` (should return PONG)
- Check Celery worker is running
- Check Celery beat is running
- Verify tasks are registered: `celery -A xshows inspect registered`

### API returns no data:
- Verify your API credentials are correct
- Check API rate limits
- Test API URL directly in browser/Postman
- Check logs for HTTP errors

## 📊 Performance Tips

1. **Batch Size**: Start with smaller limits (50-100) and increase
2. **Caching**: Consider adding Redis caching for model data
3. **Database Indexing**: Already added on model_id, user_name, gender, source
4. **Bulk Operations**: Services use `bulk_create` for efficiency
5. **Pagination**: Consider paginating large API responses

## 🎯 Next Steps

1. **Get API Credentials**: Sign up for affiliate programs
2. **Add Configs**: Create Config entries with your credentials
3. **Test Scraping**: Use `python manage.py scrape_models`
4. **Monitor**: Check Django admin and logs
5. **Enable Celery**: Set up automated scraping
6. **Fine-tune**: Adjust schedules, limits based on your needs

## 📝 Example Workflow

```bash
# 1. Add API config via Django admin
# 2. Test manually
python manage.py scrape_models chaturbate --limit 10

# 3. Check results
python manage.py shell
>>> from models_app.models import WebcamModel
>>> WebcamModel.objects.count()
10

# 4. Start Celery for automation
celery -A xshows worker -B -l info

# 5. Monitor in Django admin
# Visit http://localhost:8000/admin/models_app/webcammodel/
```

That's it! The scraping system is fully implemented and ready to use! 🎉
