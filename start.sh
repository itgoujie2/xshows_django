#!/bin/bash
# XShows Django - Start All Services

cd ~/Downloads/xshows_django

echo "🚀 Starting XShows Django..."

# Check if Redis is running
if ! ~/Downloads/redis-stable/src/redis-cli ping > /dev/null 2>&1; then
    echo "📦 Starting Redis..."
    ~/Downloads/redis-stable/src/redis-server --daemonize yes --port 6379
    sleep 1
fi

# Check if MySQL is running
if ! mysqladmin ping -h localhost -u root -pAa20130715 > /dev/null 2>&1; then
    echo "🗄️  Starting MySQL..."
    brew services start mysql
    sleep 2
fi

# Start Supervisor
echo "⚙️  Starting Supervisor (Django + Celery)..."
source venv/bin/activate
supervisord -c supervisord.conf

sleep 2

# Check status
echo ""
echo "📊 Service Status:"
supervisorctl -c supervisord.conf status

echo ""
echo "✅ All services started!"
echo "🌐 Website: http://localhost:8000/"
echo ""
echo "📝 Useful commands:"
echo "  supervisorctl -c supervisord.conf status      # Check status"
echo "  supervisorctl -c supervisord.conf restart xshows:*  # Restart all"
echo "  tail -f logs/django.log                       # View Django logs"
echo "  tail -f logs/celery-worker.log                # View Celery logs"
echo ""
