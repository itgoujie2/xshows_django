# Redis Setup for XShows Django

## What is Redis?

Redis is an in-memory data store used by Celery as a message broker. It queues background tasks so Celery workers can process them.

## Installation (Already Done)

Redis was compiled from source and is located at:
```
~/Downloads/redis-stable/
```

## Starting Redis

### Manual Start
```bash
~/Downloads/redis-stable/src/redis-server --daemonize yes --port 6379
```

### Check if Running
```bash
~/Downloads/redis-stable/src/redis-cli ping
# Should return: PONG
```

### Stop Redis
```bash
~/Downloads/redis-stable/src/redis-cli shutdown
```

## Auto-start with XShows

The `start.sh` script automatically starts Redis if it's not running:

```bash
cd ~/Downloads/xshows_django
./start.sh
```

## Redis Commands

### Connect to Redis CLI
```bash
~/Downloads/redis-stable/src/redis-cli
```

Inside CLI:
```redis
127.0.0.1:6379> PING
PONG

127.0.0.1:6379> KEYS *
# Shows all keys in Redis

127.0.0.1:6379> INFO
# Shows Redis info

127.0.0.1:6379> DBSIZE
# Shows number of keys

127.0.0.1:6379> FLUSHALL
# Clears all data (use with caution!)

127.0.0.1:6379> EXIT
```

### Monitor Celery Tasks in Real-time
```bash
~/Downloads/redis-stable/src/redis-cli MONITOR
```

This shows all commands being executed, including Celery tasks.

## Troubleshooting

### "Connection refused" error

Redis isn't running. Start it:
```bash
~/Downloads/redis-stable/src/redis-server --daemonize yes --port 6379
```

### "Address already in use"

Redis is already running or another service is using port 6379.

Check what's using the port:
```bash
lsof -i :6379
```

### Redis consuming too much memory

Check memory usage:
```bash
~/Downloads/redis-stable/src/redis-cli INFO memory
```

Clear old data:
```bash
~/Downloads/redis-stable/src/redis-cli FLUSHDB
```

### Redis logs location

By default (when started with `--daemonize yes`), Redis doesn't create a log file. To see logs:

Start without daemon mode:
```bash
~/Downloads/redis-stable/src/redis-server --port 6379
# Watch output in terminal
```

Or configure logging:
```bash
~/Downloads/redis-stable/src/redis-server --daemonize yes --logfile ~/Downloads/xshows_django/logs/redis.log
```

## Configuration File (Optional)

To customize Redis, create a config file:

```bash
nano ~/Downloads/redis-stable/redis.conf
```

Common settings:
```conf
daemonize yes
port 6379
logfile /Users/jiegou/Downloads/xshows_django/logs/redis.log
maxmemory 256mb
maxmemory-policy allkeys-lru
```

Start with config:
```bash
~/Downloads/redis-stable/src/redis-server ~/Downloads/redis-stable/redis.conf
```

## Production Considerations (AWS)

On AWS EC2, you have two options:

### Option 1: Install Redis on EC2 (Free)
```bash
sudo apt install redis-server
sudo systemctl start redis
sudo systemctl enable redis
```

### Option 2: Use AWS ElastiCache ($13/month)

Managed Redis service with:
- Automatic backups
- High availability
- Auto failover
- Monitoring

Update `.env`:
```ini
REDIS_HOST=your-elasticache-endpoint.cache.amazonaws.com
REDIS_PORT=6379
```

## Persistence

By default, Redis saves data to disk periodically. If Redis crashes or restarts, your Celery queue is preserved.

Check if data is being saved:
```bash
ls -lh ~/Downloads/redis-stable/dump.rdb
```

To force save:
```bash
~/Downloads/redis-stable/src/redis-cli SAVE
```

## Monitoring

### Check connection count
```bash
~/Downloads/redis-stable/src/redis-cli INFO clients
```

### Check memory usage
```bash
~/Downloads/redis-stable/src/redis-cli INFO memory
```

### Check Celery queue length
```bash
~/Downloads/redis-stable/src/redis-cli LLEN celery
```

## Quick Reference

```bash
# Start
~/Downloads/redis-stable/src/redis-server --daemonize yes --port 6379

# Check status
~/Downloads/redis-stable/src/redis-cli ping

# Connect
~/Downloads/redis-stable/src/redis-cli

# Stop
~/Downloads/redis-stable/src/redis-cli shutdown

# Monitor activity
~/Downloads/redis-stable/src/redis-cli MONITOR

# View logs (if configured)
tail -f ~/Downloads/xshows_django/logs/redis.log
```

## Integration with XShows

Redis is configured in `xshows/settings.py`:

```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
```

Celery uses Redis to:
1. Queue tasks (e.g., `update_chaturbate_data`)
2. Store task results
3. Schedule periodic tasks (via Celery Beat)

## Useful Aliases

Add to your `~/.zshrc` or `~/.bashrc`:

```bash
alias redis-start='~/Downloads/redis-stable/src/redis-server --daemonize yes --port 6379'
alias redis-stop='~/Downloads/redis-stable/src/redis-cli shutdown'
alias redis-cli='~/Downloads/redis-stable/src/redis-cli'
alias redis-status='~/Downloads/redis-stable/src/redis-cli ping'
```

Then use:
```bash
redis-start
redis-status
redis-cli
```

## Next Steps

✅ Redis is running
✅ Celery is connected
✅ Scheduled tasks are working

You're all set! The scraping will happen automatically every 30 minutes.
