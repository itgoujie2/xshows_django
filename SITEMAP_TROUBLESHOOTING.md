# Sitemap Troubleshooting Guide

## Issue: "Your Sitemap appears to be an HTML page"

The sitemap is generating correctly in the codebase. Here's how to fix it on your production server:

---

## Quick Fixes (Try These First)

### 1. Clear Browser Cache
- Hard refresh: `Ctrl+F5` (Windows) or `Cmd+Shift+R` (Mac)
- Or open in incognito/private browsing mode
- Try: `curl -I https://nakedalerts.com/sitemap.xml` to see raw headers

### 2. Restart Django Server
```bash
# If using supervisor
sudo supervisorctl restart xshows

# If using systemd
sudo systemctl restart your-django-service

# If using gunicorn/uwsgi directly
sudo systemctl restart gunicorn
# or
sudo pkill -HUP gunicorn
```

### 3. Clear Application Cache
```bash
source venv/bin/activate
python manage.py shell << 'EOF'
from django.core.cache import cache
cache.clear()
print("Cache cleared!")
EOF
```

---

## Verify Sitemap is Working

### Test Locally First:
```bash
# SSH into your server
cd /path/to/xshows_django
source venv/bin/activate

# Test the sitemap
python manage.py shell << 'EOF'
from django.test import Client
client = Client()
response = client.get('/sitemap.xml')
print(f"Status: {response.status_code}")
print(f"Content-Type: {response.get('Content-Type')}")
print(f"First 200 chars: {response.content.decode('utf-8')[:200]}")
EOF
```

Expected output:
```
Status: 200
Content-Type: application/xml
First 200 chars: <?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"...
```

### Test via HTTP:
```bash
# From your server
curl -H "Host: nakedalerts.com" http://localhost:8000/sitemap.xml | head -20

# From outside
curl -I https://nakedalerts.com/sitemap.xml
```

Look for: `Content-Type: application/xml`

---

## Common Issues & Solutions

### Issue 1: Nginx/Apache Caching

If you're using nginx or Apache, they might be caching the old response.

**Nginx Fix:**
```nginx
# Add to your nginx config
location = /sitemap.xml {
    proxy_pass http://your-backend;
    proxy_cache_bypass $http_pragma $http_authorization;
    add_header Cache-Control "public, max-age=3600";
}
```

Then:
```bash
sudo nginx -t
sudo systemctl reload nginx
```

**Apache Fix:**
```apache
# Add to .htaccess or apache config
<Files "sitemap.xml">
    Header set Cache-Control "max-age=3600, public"
</Files>
```

### Issue 2: Django APPEND_SLASH Redirecting

Make sure the URL doesn't have a trailing slash:

✅ Correct: `https://nakedalerts.com/sitemap.xml`
❌ Wrong: `https://nakedalerts.com/sitemap.xml/`

### Issue 3: Site Domain Not Set

Update your Site domain in the database:

```bash
source venv/bin/activate
python manage.py shell << 'EOF'
from django.contrib.sites.models import Site
site = Site.objects.get(pk=1)
site.domain = 'nakedalerts.com'
site.name = 'NakedAlerts'
site.save()
print(f"Site updated: {site.domain}")
EOF
```

### Issue 4: Static File Serving Conflict

Make sure nginx/Apache isn't trying to serve sitemap.xml as a static file:

**Nginx:**
```nginx
# Make sure sitemap.xml is NOT in this location block
location /static/ {
    alias /path/to/staticfiles/;
}

# Add explicit proxy for sitemap before static
location = /sitemap.xml {
    proxy_pass http://127.0.0.1:8000;
}
```

### Issue 5: Wrong Python Environment

Make sure your production server is using the correct virtual environment:

```bash
# Check which Python is running
which python
# Should point to your venv

# Verify Django version
python -c "import django; print(django.get_version())"

# Check if sitemaps app is installed
python -c "from django.contrib.sitemaps import Sitemap; print('OK')"
```

---

## Debugging Steps

### Step 1: Check URL Routing
```bash
source venv/bin/activate
python manage.py show_urls | grep sitemap
```

Expected output:
```
/sitemap.xml   django.contrib.sitemaps.views.sitemap
```

### Step 2: Check for Errors
```bash
# Check Django logs
tail -f /var/log/your-app/error.log

# Check nginx logs
sudo tail -f /var/log/nginx/error.log
```

### Step 3: Test Direct Django Response
```bash
# Bypass nginx/apache and test Django directly
curl http://127.0.0.1:8000/sitemap.xml
```

If this returns XML but the public URL returns HTML, the issue is with your web server (nginx/apache).

### Step 4: Check Response Headers
```bash
curl -v https://nakedalerts.com/sitemap.xml 2>&1 | grep -i "content-type"
```

Should show: `Content-Type: application/xml`

---

## Production Deployment Checklist

After making changes, deploy properly:

```bash
# 1. Pull latest code
git pull origin main

# 2. Activate virtual environment
source venv/bin/activate

# 3. Install any new dependencies (if needed)
pip install -r requirements.txt

# 4. Run migrations (if any)
python manage.py migrate

# 5. Collect static files (if needed)
python manage.py collectstatic --noinput

# 6. Update Site domain
python manage.py shell << 'EOF'
from django.contrib.sites.models import Site
site = Site.objects.get_or_create(pk=1, defaults={'domain': 'nakedalerts.com', 'name': 'NakedAlerts'})[0]
site.domain = 'nakedalerts.com'
site.name = 'NakedAlerts'
site.save()
EOF

# 7. Restart application
sudo supervisorctl restart xshows
# or your restart command

# 8. Reload web server
sudo systemctl reload nginx
```

---

## Verify It's Fixed

### Test 1: HTTP Headers
```bash
curl -I https://nakedalerts.com/sitemap.xml
```

Should see:
```
HTTP/2 200
Content-Type: application/xml
```

### Test 2: XML Content
```bash
curl https://nakedalerts.com/sitemap.xml | head -5
```

Should see:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" ...>
```

### Test 3: Google Search Console
1. Go to: https://search.google.com/search-console
2. Click on your property (nakedalerts.com)
3. Go to "Sitemaps" in the left menu
4. Enter: `sitemap.xml`
5. Click "Submit"
6. Check status - should show "Success"

---

## Still Having Issues?

### Check Django Settings

Verify in `settings.py`:
```python
INSTALLED_APPS = [
    # ...
    'django.contrib.sites',
    'django.contrib.sitemaps',
    # ...
]

SITE_ID = 1
```

### Check URLs Configuration

Verify in `xshows/urls.py`:
```python
from django.contrib.sitemaps.views import sitemap
from sitemaps import (
    StaticViewSitemap,
    CategorySitemap,
    GenderSitemap,
    ModelDetailSitemap,
    OnlineModelsSitemap,
    NakedModelsSitemap,
)

sitemaps = {
    'static': StaticViewSitemap,
    'categories': CategorySitemap,
    'genders': GenderSitemap,
    'models': ModelDetailSitemap,
    'online': OnlineModelsSitemap,
    'naked': NakedModelsSitemap,
}

urlpatterns = [
    # THIS MUST BE FIRST!
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    # ... other URLs
]
```

---

## Force Regenerate Sitemap

If caching is causing issues, you can force regenerate:

```bash
source venv/bin/activate
python manage.py shell << 'EOF'
from django.contrib.sitemaps import views
from sitemaps import *

# This will trigger regeneration
sitemaps = {
    'static': StaticViewSitemap,
    'categories': CategorySitemap,
    'genders': GenderSitemap,
    'models': ModelDetailSitemap,
    'online': OnlineModelsSitemap,
    'naked': NakedModelsSitemap,
}

print("Sitemaps registered:")
for name, sitemap_class in sitemaps.items():
    print(f"  - {name}: {len(sitemap_class().items())} items")
EOF
```

---

## Contact Support

If none of these solutions work, gather this information:

1. Output of: `curl -I https://nakedalerts.com/sitemap.xml`
2. Output of: `curl https://nakedalerts.com/sitemap.xml | head -20`
3. Django version: `python -c "import django; print(django.get_version())"`
4. Any error messages from Django logs
5. Your nginx/apache configuration (if applicable)

Then post in Django forums or create a GitHub issue with this information.

---

## Success Indicators

You'll know it's working when:

✅ `curl https://nakedalerts.com/sitemap.xml` returns XML starting with `<?xml`
✅ Content-Type header is `application/xml`
✅ Google Search Console accepts the sitemap without errors
✅ Google starts indexing your pages (check in a few days)

---

## Next Steps After Fix

Once your sitemap is working:

1. **Submit to Google Search Console**
   - URL: https://search.google.com/search-console
   - Add sitemap: `https://nakedalerts.com/sitemap.xml`

2. **Submit to Bing Webmaster Tools**
   - URL: https://www.bing.com/webmasters
   - Add sitemap: `https://nakedalerts.com/sitemap.xml`

3. **Monitor Indexing**
   - Check Google Search Console weekly
   - See which pages are being indexed
   - Fix any crawl errors

4. **Update Regularly**
   - Sitemap updates automatically as models go online/offline
   - No manual intervention needed
   - Google will re-crawl periodically

---

Good luck! Your sitemap should be working now. 🎉
