# Local Supervisor Setup Guide

This guide shows you how to use Supervisor locally on macOS to manage Django + Celery processes.

## What is Supervisor?

Supervisor is a process control system that:
- Runs multiple services in the background
- Auto-restarts them if they crash
- Provides a single interface to start/stop/monitor all services
- Persists even after you close your terminal

## Installation

Supervisor is already installed via Homebrew. Verify with:

```bash
supervisord --version
```

## Configuration

The `supervisord.conf` file in your project root manages these services:

1. **xshows-django** - Django development server on port 8000
2. **xshows-celery-worker** - Celery worker for background tasks
3. **xshows-celery-beat** - Celery scheduler for periodic tasks

## Usage

### Starting Supervisor

```bash
cd ~/Downloads/xshows_django
supervisord -c supervisord.conf
```

This starts all services in the background. You can close your terminal and they'll keep running.

### Checking Status

```bash
cd ~/Downloads/xshows_django
supervisorctl -c supervisord.conf status
```

Expected output:
```
xshows-celery-beat          RUNNING   pid 12345, uptime 0:05:23
xshows-celery-worker        RUNNING   pid 12346, uptime 0:05:23
xshows-django               RUNNING   pid 12347, uptime 0:05:23
```

### Interactive Control

```bash
cd ~/Downloads/xshows_django
supervisorctl -c supervisord.conf
```

This opens an interactive shell where you can:

```bash
supervisor> status                    # Show status
supervisor> start xshows:*            # Start all services
supervisor> stop xshows:*             # Stop all services
supervisor> restart xshows:*          # Restart all services
supervisor> restart xshows-django     # Restart specific service
supervisor> tail -f xshows-django     # View live logs
supervisor> help                      # Show all commands
supervisor> quit                      # Exit
```

### One-line Commands

```bash
# Stop all services
supervisorctl -c supervisord.conf stop xshows:*

# Start all services
supervisorctl -c supervisord.conf start xshows:*

# Restart all services
supervisorctl -c supervisord.conf restart xshows:*

# Restart just Django
supervisorctl -c supervisord.conf restart xshows-django

# Restart just Celery worker
supervisorctl -c supervisord.conf restart xshows-celery-worker
```

### Viewing Logs

```bash
# View Django logs
tail -f ~/Downloads/xshows_django/logs/django.log

# View Celery worker logs
tail -f ~/Downloads/xshows_django/logs/celery-worker.log

# View Celery beat logs
tail -f ~/Downloads/xshows_django/logs/celery-beat.log

# View supervisor logs
tail -f ~/Downloads/xshows_django/logs/supervisord.log
```

Or use supervisorctl:
```bash
supervisorctl -c supervisord.conf tail -f xshows-django
supervisorctl -c supervisord.conf tail -f xshows-celery-worker
```

### Stopping Supervisor

```bash
# Stop all services
supervisorctl -c supervisord.conf stop xshows:*

# Shutdown supervisor daemon
supervisorctl -c supervisord.conf shutdown
```

Or kill it:
```bash
kill $(cat ~/Downloads/xshows_django/supervisord.pid)
```

## Common Workflows

### 1. Start Everything in Background

```bash
cd ~/Downloads/xshows_django
supervisord -c supervisord.conf
```

Now Django + Celery are running. Visit http://localhost:8000/

### 2. Check if Everything is Running

```bash
supervisorctl -c supervisord.conf status
```

### 3. Update Code and Restart

```bash
# After editing code
supervisorctl -c supervisord.conf restart xshows-django
```

### 4. Stop Everything and Work Normally

```bash
supervisorctl -c supervisord.conf shutdown
python manage.py runserver  # Back to manual mode
```

### 5. Daily Development Workflow

**Morning:**
```bash
cd ~/Downloads/xshows_django
supervisord -c supervisord.conf
# Everything runs in background, work on other things
```

**During work:**
```bash
# Edit code...
supervisorctl -c supervisord.conf restart xshows-django  # After changes
```

**Evening:**
```bash
supervisorctl -c supervisord.conf shutdown  # Or leave it running!
```

## Advantages vs Terminal Windows

| Terminal Windows | Supervisor |
|------------------|------------|
| Need 3 terminals open | Just 1 command |
| Closes when terminal closes | Runs in background |
| Must manually restart | Auto-restarts on crash |
| Hard to manage logs | Centralized logging |
| Easy to forget what's running | `status` command shows all |

## Troubleshooting

### "unix:///path/supervisor.sock refused connection"

Supervisor isn't running. Start it:
```bash
supervisord -c supervisord.conf
```

### "ERROR: Another program is already listening on port 8000"

Something else is using port 8000 (maybe you ran `python manage.py runserver` manually).

Find and kill it:
```bash
lsof -ti:8000 | xargs kill -9
```

Then restart supervisor:
```bash
supervisorctl -c supervisord.conf restart xshows-django
```

### "unix:///path/supervisor.sock no such file"

The sock file gets deleted sometimes. Just restart:
```bash
supervisord -c supervisord.conf
```

### Service shows "FATAL" or "EXITED"

Check the logs:
```bash
supervisorctl -c supervisord.conf tail xshows-django
# Or
tail -f logs/django.log
```

Common causes:
- Virtual environment not activated (check `environment=PATH=` in config)
- MySQL not running (`brew services start mysql`)
- Redis not running (`brew services start redis`)

### Can't stop supervisord

```bash
# Find the PID
cat ~/Downloads/xshows_django/supervisord.pid

# Kill it
kill -9 <PID>

# Clean up
rm ~/Downloads/xshows_django/supervisord.pid
rm ~/Downloads/xshows_django/supervisor.sock
```

## Configuration Changes

After modifying `supervisord.conf`:

```bash
# Reload configuration
supervisorctl -c supervisord.conf reread
supervisorctl -c supervisord.conf update

# Or just restart supervisor
supervisorctl -c supervisord.conf shutdown
supervisord -c supervisord.conf
```

## Auto-start on macOS Boot (Optional)

To start supervisor automatically when you login:

```bash
# Create LaunchAgent
mkdir -p ~/Library/LaunchAgents

cat > ~/Library/LaunchAgents/com.xshows.supervisor.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.xshows.supervisor</string>
    <key>ProgramArguments</key>
    <array>
        <string>/opt/homebrew/bin/supervisord</string>
        <string>-c</string>
        <string>/Users/jiegou/Downloads/xshows_django/supervisord.conf</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/jiegou/Downloads/xshows_django/logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/jiegou/Downloads/xshows_django/logs/launchd-error.log</string>
</dict>
</plist>
EOF

# Load it
launchctl load ~/Library/LaunchAgents/com.xshows.supervisor.plist

# To disable auto-start:
launchctl unload ~/Library/LaunchAgents/com.xshows.supervisor.plist
```

## Comparison: Manual vs Supervisor

### Manual (3 terminals)
```bash
# Terminal 1
cd ~/Downloads/xshows_django
source venv/bin/activate
python manage.py runserver

# Terminal 2
cd ~/Downloads/xshows_django
source venv/bin/activate
celery -A xshows worker -l info

# Terminal 3
cd ~/Downloads/xshows_django
source venv/bin/activate
celery -A xshows beat -l info
```

### Supervisor (1 command)
```bash
cd ~/Downloads/xshows_django
supervisord -c supervisord.conf
# Done! All 3 services running in background
```

## Quick Reference

```bash
# Start
supervisord -c supervisord.conf

# Status
supervisorctl -c supervisord.conf status

# Restart all
supervisorctl -c supervisord.conf restart xshows:*

# Stop all
supervisorctl -c supervisord.conf stop xshows:*

# Shutdown
supervisorctl -c supervisord.conf shutdown

# Logs
tail -f logs/django.log
tail -f logs/celery-worker.log
tail -f logs/celery-beat.log
```

## Tips

1. **Alias for convenience**: Add to `~/.zshrc`:
   ```bash
   alias xsup='supervisorctl -c ~/Downloads/xshows_django/supervisord.conf'
   ```
   Then use: `xsup status`, `xsup restart xshows:*`

2. **Log rotation**: Logs are automatically rotated (10MB max, 3 backups)

3. **Development vs Production**:
   - This config uses `runserver` for development
   - AWS config uses `gunicorn` for production

4. **Redis required**: Make sure Redis is running:
   ```bash
   brew services start redis
   ```

5. **MySQL required**: Make sure MySQL is running:
   ```bash
   brew services start mysql
   ```

## Next Steps

Once you're comfortable with Supervisor locally, you'll use the exact same commands on AWS EC2:

```bash
# On EC2 (production)
sudo supervisorctl status
sudo supervisorctl restart xshows:*
```

The only difference is configuration paths and using `sudo`.
