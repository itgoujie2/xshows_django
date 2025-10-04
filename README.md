# XShows Django

A Django-based webcam model aggregator platform, converted from Laravel/PHP to Django/Python.

## Overview

XShows Django is a web application that aggregates webcam models from multiple streaming platforms including Stripcash, Chaturbate, XLoveCash, and BongaCash. The application provides:

- User authentication and registration
- Model browsing and filtering by category/gender
- Favourites system for registered users
- Admin panel for content management
- Background jobs for scraping and updating model data
- RESTful API support

## Technology Stack

- **Framework**: Django 4.2
- **Python**: 3.9+
- **Database**: MySQL
- **Task Queue**: Celery with Redis
- **Authentication**: django-allauth
- **API**: Django REST Framework
- **Admin**: Django Admin + custom admin panel

## Project Structure

```
xshows_django/
├── admin_panel/         # Admin panel app for management
├── categories/          # Categories app
├── core/                # Core app (home views, configs)
├── models_app/          # Webcam models app
├── users/               # User authentication app
├── xshows/              # Main project settings
├── static/              # Static files (CSS, JS, images)
├── media/               # Uploaded media files
├── templates/           # Django templates
├── manage.py            # Django management script
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables
```

## Installation

### Prerequisites

- Python 3.9 or higher
- MySQL database
- Redis server (for Celery)

### Setup Steps

1. **Clone or navigate to the project directory**:
   ```bash
   cd ~/Downloads/xshows_django
   ```

2. **Create and activate virtual environment**:
   ```bash
   python3.9 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**:
   Edit the `.env` file with your database credentials and other settings:
   ```bash
   DB_DATABASE=xshows
   DB_USERNAME=root
   DB_PASSWORD=your_password
   SECRET_KEY=your-secret-key-here
   ```

5. **Run migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create superuser**:
   ```bash
   python manage.py createsuperuser
   ```

7. **Collect static files**:
   ```bash
   python manage.py collectstatic
   ```

8. **Run development server**:
   ```bash
   python manage.py runserver
   ```

   Visit http://localhost:8000

## Background Tasks

### Start Celery Worker

```bash
celery -A xshows worker -l info
```

### Start Celery Beat (for scheduled tasks)

```bash
celery -A xshows beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
```

### Scheduled Tasks

- **Data Updates**: Every 30 minutes
  - Update Stripcash models
  - Update Chaturbate models
  - Update XLoveCash models
  - Update BongaCash models

- **Status Updates**: Every 5 minutes
  - Update online/offline status for all models

## Database Models

### Core Models

- **User**: Custom user model with role-based access (admin/member)
- **Config**: API configuration for external platforms
- **Setting**: Application settings

### Content Models

- **WebcamModel**: Webcam performers from various platforms
- **Category**: Content categories with SEO fields
- **ModelCategory**: Many-to-many through table
- **Favourite**: User favourites
- **XLoveCashTag**: Tags from XLoveCash platform

## API Endpoints

- `/admin/` - Django admin interface
- `/admin-panel/` - Custom admin panel
- `/accounts/` - Authentication (login, register, password reset)
- `/chat/<username>/` - Model detail page
- `/gender/<sex>/` - Filter by gender
- `/favorites/` - User favourites
- `/<category>/` - Filter by category

## Admin Panel

Access the admin panel at `/admin-panel/` with admin credentials.

Features:
- User management
- Category management
- Config management
- Settings management
- Statistics dashboard

## Configuration

### Database

Configure in `.env`:
```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_DATABASE=xshows
DB_USERNAME=root
DB_PASSWORD=
```

### Email

Configure SMTP settings in `.env`:
```
MAIL_HOST=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

### Redis/Celery

```
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

## Differences from Laravel Version

1. **ORM**: Eloquent → Django ORM
2. **Templates**: Blade → Django Templates
3. **Routing**: Laravel routes → Django URLconf
4. **Middleware**: Laravel middleware → Django middleware
5. **Background Jobs**: Laravel Queue → Celery
6. **Authentication**: Laravel Auth → django-allauth
7. **Database Migrations**: Laravel migrations → Django migrations

## Development Notes

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Running Tests

```bash
python manage.py test
```

### Shell Access

```bash
python manage.py shell
```

## Deployment

For production deployment:

1. Set `DEBUG=False` in `.env`
2. Configure `ALLOWED_HOSTS`
3. Set up proper database credentials
4. Configure static files serving (nginx/Apache)
5. Use production-grade WSGI server (gunicorn/uwsgi)
6. Set up SSL certificates
7. Configure Redis for production
8. Set up Celery as a system service

## Migration from Laravel

This project was converted from a Laravel 7 PHP application. Key conversions:

- ✅ Database models and relationships
- ✅ Authentication system
- ✅ Admin panel structure
- ✅ URL routing
- ✅ Background jobs (Celery tasks)
- ✅ Configuration management
- ⏳ Blade templates → Django templates (requires conversion)
- ⏳ Complete task implementations

## Contributing

1. Follow Django best practices
2. Use class-based views where appropriate
3. Write tests for new features
4. Document API endpoints
5. Keep migrations clean and reversible

## License

MIT License (same as Laravel version)

## Support

For issues or questions, please refer to the Django documentation:
- https://docs.djangoproject.com/
- https://www.django-rest-framework.org/
- https://docs.celeryproject.org/
