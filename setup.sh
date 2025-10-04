#!/bin/bash
# Setup script for XShows Django project

echo "========================================="
echo "XShows Django Setup Script"
echo "========================================="
echo ""

# Check Python version
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Activate virtual environment
echo ""
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "ERROR: .env file not found!"
    echo "Please create .env file with your configuration."
    exit 1
fi

# Run migrations
echo ""
echo "Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser prompt
echo ""
read -p "Do you want to create a superuser? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    python manage.py createsuperuser
fi

# Collect static files
echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "========================================="
echo "Setup completed!"
echo "========================================="
echo ""
echo "To start the development server:"
echo "  python manage.py runserver"
echo ""
echo "To start Celery worker:"
echo "  celery -A xshows worker -l info"
echo ""
echo "To start Celery beat:"
echo "  celery -A xshows beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler"
echo ""
