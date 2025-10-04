# Quick Start Guide

## ✅ What's Been Done

Your Laravel project has been successfully converted to Django! Here's what we've completed:

- ✅ Django project structure created
- ✅ All database models converted
- ✅ All controllers converted to views
- ✅ All routes converted to URLs
- ✅ Celery background tasks configured
- ✅ **All main templates converted from Blade to Django**
- ✅ Context processors for global variables
- ✅ Admin interface configured
- ✅ Authentication system ready

## 🚀 Get It Running (Step by Step)

### Step 1: Create MySQL Database

```bash
# Log into MySQL
mysql -u root -p

# Create the database
CREATE DATABASE xshows CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
EXIT;
```

### Step 2: Configure Database

Edit `.env` file:
```bash
cd ~/Downloads/xshows_django
nano .env
```

Update these lines with your MySQL credentials:
```
DB_PASSWORD=your_mysql_password
DB_USERNAME=root
DB_DATABASE=xshows
```

Save and exit (Ctrl+X, then Y, then Enter)

### Step 3: Run Migrations

```bash
cd ~/Downloads/xshows_django
source venv/bin/activate
python manage.py migrate
```

### Step 4: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts:
- Username: admin (or whatever you want)
- Email: your@email.com
- Password: (choose a password)

### Step 5: Create Some Test Data

```bash
python manage.py shell
```

Then in the Python shell:
```python
from categories.models import Category

# Create test categories
Category.objects.create(
    name='asian',
    display_name='Asian',
    is_active=True,
    description='Asian models',
    keywords='asian, webcam, live',
    title='Asian Cams'
)

Category.objects.create(
    name='ebony',
    display_name='Ebony',
    is_active=True,
    description='Ebony models',
    keywords='ebony, webcam, live',
    title='Ebony Cams'
)

Category.objects.create(
    name='latina',
    display_name='Latina',
    is_active=True,
    description='Latina models',
    keywords='latina, webcam, live',
    title='Latina Cams'
)

# Exit shell
exit()
```

### Step 6: Start the Server

```bash
python manage.py runserver
```

### Step 7: Visit Your Site! 🎉

Open your browser and go to:
- **Home Page**: http://localhost:8000/
- **Admin Panel**: http://localhost:8000/admin/
- **Django Admin**: http://localhost:8000/admin/ (Django's built-in admin)

## 📋 What Works Now

### Working Pages:
- ✅ Home page (/)
- ✅ Login page (/login/)
- ✅ Register page (/register/)
- ✅ Gender filter pages (/gender/female/, /gender/male/, /gender/trans/)
- ✅ Category pages (/asian/, /ebony/, etc.)
- ✅ Favorites page (/favorites/) - requires login
- ✅ Django admin (/admin/)

### Not Yet Working (Need Data):
- Model detail pages - need actual model data
- Scraping tasks - stubs created, logic needs implementation

## 🎯 Next Steps

### Option A: Add Test Models Manually

Via Django Admin (http://localhost:8000/admin/):
1. Login with your superuser credentials
2. Go to "Webcam Models"
3. Click "Add Webcam Model"
4. Fill in the fields (minimum required: model_id, user_name, display_name, image URL, source, json_data as `{}`)

### Option B: Migrate Existing Laravel Data

If you have data in your Laravel database:
```bash
# Export from Laravel MySQL
mysqldump -u root -p your_laravel_db models categories users > backup.sql

# Import to Django MySQL (adjust table names if needed)
mysql -u root -p xshows < backup.sql
```

### Option C: Implement Scraping Tasks

The Celery tasks are created but need scraping logic:
1. Open `models_app/tasks.py`
2. Implement the scraping functions using Python `requests` library
3. Start Celery: `celery -A xshows worker -l info`

## 🔧 Troubleshooting

### "No such table" error
```bash
python manage.py migrate
```

### Static files not loading
```bash
python manage.py collectstatic
```

### Can't connect to database
- Check MySQL is running: `mysql -u root -p`
- Check `.env` file has correct credentials
- Make sure database exists: `SHOW DATABASES;` in MySQL

### Import errors
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 📁 Project Structure

```
xshows_django/
├── templates/              ← All converted Blade templates
│   ├── base.html          ← Base layout
│   ├── core/              ← Home page templates
│   ├── models_app/        ← Model pages
│   ├── users/             ← Auth templates
│   └── partials/          ← Reusable components
├── static/                ← CSS, JS, images (copied from Laravel)
├── core/                  ← Core app (home, settings)
├── users/                 ← User authentication
├── models_app/            ← Webcam models
├── categories/            ← Categories
├── admin_panel/           ← Admin panel
└── xshows/                ← Project settings
```

## 🎨 Customization

### Change Site Title
Edit `core/context_processors.py`:
```python
'site_title': 'Your Site Name Here',
```

### Add More Categories
Via Django shell or Admin panel

### Customize Templates
Templates are in `templates/` directory - edit any `.html` file

## ✨ Features Ready to Use

1. **User Authentication**: Registration, login, password reset
2. **Favorites System**: Users can favorite models
3. **Category Filtering**: Browse by category
4. **Gender Filtering**: Filter by trans/male/female
5. **Admin Panel**: Manage users, categories, settings
6. **Pagination**: Automatically paginated model lists
7. **Responsive Design**: Bootstrap 4 responsive layout

## 🐛 Known Limitations

1. **No Live Data Yet**: Need to implement scraping or add data manually
2. **Admin Panel Templates**: Basic admin templates created, may need styling
3. **Live Iframes**: Platform-specific iframe logic needs implementation
4. **Search**: Not yet implemented (easy to add)

## 💪 You're All Set!

Your site should now be running at http://localhost:8000

The hard work is done - models, views, templates are all converted. Now you just need to:
1. Add some data (manually or via scraping)
2. Customize the look if needed
3. Deploy when ready!

Questions? Check:
- `README.md` - Full documentation
- `CONVERSION_NOTES.md` - Conversion details
- `TEMPLATES_CREATED.md` - Template conversion guide
