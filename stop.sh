#!/bin/bash
# XShows Django - Stop All Services

cd ~/Downloads/xshows_django

echo "🛑 Stopping XShows Django..."

# Stop Supervisor
if [ -f supervisord.pid ]; then
    echo "⚙️  Stopping Supervisor (Django + Celery)..."
    source venv/bin/activate
    supervisorctl -c supervisord.conf shutdown
    sleep 2
fi

# Stop Redis (optional - comment out if you want Redis to keep running)
# echo "📦 Stopping Redis..."
# ~/Downloads/redis-stable/src/redis-cli shutdown

echo ""
echo "✅ All services stopped!"
