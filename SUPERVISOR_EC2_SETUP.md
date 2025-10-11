# Supervisor Setup Guide for Amazon Linux 2023

Complete step-by-step guide to set up Supervisor on EC2 Amazon Linux 2023 from scratch.

---

## Prerequisites

- Fresh Amazon Linux 2023 EC2 instance
- Python 3.11 installed
- Project deployed at `/var/www/xshows`

---

## Step 1: Install Supervisor

```bash
# Install supervisor via pip (not available in dnf repos)
sudo pip3.11 install supervisor

# Verify installation
which supervisord
which supervisorctl
```

---

## Step 2: Create Configuration Directory

```bash
# Create directory for program configs
sudo mkdir -p /etc/supervisord.d

# Create log directory for your app
sudo mkdir -p /var/log/xshows
sudo chown ec2-user:ec2-user /var/log/xshows
```

---

## Step 3: Generate Base Configuration

```bash
# Generate default config
echo_supervisord_conf | sudo tee /etc/supervisord.conf
```

---

## Step 4: Edit Main Configuration

```bash
sudo nano /etc/supervisord.conf
```

### Make these changes:

**1. Update socket paths (find near top of file):**

```ini
[unix_http_server]
file=/tmp/supervisord.sock
chmod=0700

[supervisorctl]
serverurl=unix:///tmp/supervisord.sock
```

**2. Update log path (find [supervisord] section):**

```ini
[supervisord]
logfile=/var/log/supervisord.log
logfile_maxbytes=50MB
logfile_backups=10
loglevel=info
pidfile=/tmp/supervisord.pid
nodaemon=false
minfds=1024
minprocs=200
```

**3. Add include directive at the VERY BOTTOM:**

```ini
[include]
files = /etc/supervisord.d/*.ini
```

Save and exit (`Ctrl+X`, `Y`, `Enter`)

---

## Step 5: Create Your App Configuration

```bash
sudo nano /etc/supervisord.d/xshows.ini
```

**Paste this complete configuration:**

```ini
[program:xshows-gunicorn]
command=/var/www/xshows/venv/bin/gunicorn xshows.wsgi:application --bind 127.0.0.1:8000 --workers 2 --timeout 120
directory=/var/www/xshows
user=ec2-user
autostart=true
autorestart=true
stdout_logfile=/var/log/xshows/gunicorn.log
stderr_logfile=/var/log/xshows/gunicorn-error.log
stdout_logfile_maxbytes=10MB
stderr_logfile_maxbytes=10MB
stdout_logfile_backups=3
stderr_logfile_backups=3
environment=PATH="/var/www/xshows/venv/bin"

[program:xshows-celery-worker]
command=/var/www/xshows/venv/bin/celery -A xshows worker -l info --concurrency=2 --max-tasks-per-child=50
directory=/var/www/xshows
user=ec2-user
autostart=true
autorestart=true
stdout_logfile=/var/log/xshows/celery-worker.log
stderr_logfile=/var/log/xshows/celery-worker-error.log
stdout_logfile_maxbytes=10MB
stderr_logfile_maxbytes=10MB
stdout_logfile_backups=3
stderr_logfile_backups=3
environment=PATH="/var/www/xshows/venv/bin"
stopwaitsecs=600
stopasgroup=true
killasgroup=true

[program:xshows-celery-beat]
command=/var/www/xshows/venv/bin/celery -A xshows beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
directory=/var/www/xshows
user=ec2-user
autostart=true
autorestart=true
stdout_logfile=/var/log/xshows/celery-beat.log
stderr_logfile=/var/log/xshows/celery-beat-error.log
stdout_logfile_maxbytes=10MB
stderr_logfile_maxbytes=10MB
stdout_logfile_backups=3
stderr_logfile_backups=3
environment=PATH="/var/www/xshows/venv/bin"

[group:xshows]
programs=xshows-gunicorn,xshows-celery-worker,xshows-celery-beat
```

Save and exit.

---

## Step 6: Create Systemd Service

```bash
sudo nano /etc/systemd/system/supervisord.service
```

**Paste this:**

```ini
[Unit]
Description=Supervisor process control system
After=network.target

[Service]
Type=forking
ExecStart=/usr/local/bin/supervisord -c /etc/supervisord.conf
ExecStop=/usr/local/bin/supervisorctl -c /etc/supervisord.conf shutdown
ExecReload=/usr/local/bin/supervisorctl -c /etc/supervisord.conf reload
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

Save and exit.

---

## Step 7: Enable and Start Supervisor

```bash
# Reload systemd to recognize new service
sudo systemctl daemon-reload

# Enable supervisor to start on boot
sudo systemctl enable supervisord

# Start supervisor
sudo systemctl start supervisord

# Check status
sudo systemctl status supervisord
```

Should show: **"active (running)"**

---

## Step 8: Verify Everything Works

```bash
# Check if socket was created
ls -la /tmp/supervisord.sock

# Check supervisor status
sudo supervisorctl -c /etc/supervisord.conf status

# Should show:
# xshows-celery-beat          RUNNING   pid 12345, uptime 0:00:10
# xshows-celery-worker        RUNNING   pid 12346, uptime 0:00:10
# xshows-gunicorn             RUNNING   pid 12347, uptime 0:00:10

# Check logs
sudo tail -f /var/log/xshows/gunicorn.log
sudo tail -f /var/log/xshows/celery-worker.log
```

---

## Common Commands

### Basic Control

```bash
# Check status
sudo supervisorctl -c /etc/supervisord.conf status

# Start all programs
sudo supervisorctl -c /etc/supervisord.conf start xshows:*

# Stop all programs
sudo supervisorctl -c /etc/supervisord.conf stop xshows:*

# Restart all programs
sudo supervisorctl -c /etc/supervisord.conf restart xshows:*

# Restart specific program
sudo supervisorctl -c /etc/supervisord.conf restart xshows-gunicorn
```

### After Config Changes

```bash
# Reload config
sudo supervisorctl -c /etc/supervisord.conf reread

# Apply changes
sudo supervisorctl -c /etc/supervisord.conf update

# Restart affected programs
sudo supervisorctl -c /etc/supervisord.conf restart xshows:*
```

### View Logs

```bash
# View supervisor main log
sudo tail -f /var/log/supervisord.log

# View program logs
sudo supervisorctl -c /etc/supervisord.conf tail -f xshows-gunicorn
sudo supervisorctl -c /etc/supervisord.conf tail -f xshows-celery-worker

# Or directly
sudo tail -f /var/log/xshows/gunicorn.log
```

### Systemd Control

```bash
# Start/stop/restart supervisor service
sudo systemctl start supervisord
sudo systemctl stop supervisord
sudo systemctl restart supervisord

# Check service status
sudo systemctl status supervisord

# View service logs
sudo journalctl -u supervisord -f
```

---

## Troubleshooting

### Issue: "unix:///tmp/supervisord.sock no such file"

**Cause:** Supervisor isn't running or socket path is wrong.

**Fix:**
```bash
# Check if supervisord is running
ps aux | grep supervisord

# If not running, start it
sudo systemctl start supervisord

# Verify socket was created
ls -la /tmp/supervisord.sock

# Check for errors
sudo journalctl -u supervisord -n 50
```

---

### Issue: "No config updates to processes" after reread

**Cause:** Config already loaded or no changes made.

**Fix:**
```bash
# This is normal if config hasn't changed
# Just check status
sudo supervisorctl -c /etc/supervisord.conf status

# If programs aren't listed, check include directive
sudo grep -A2 "\[include\]" /etc/supervisord.conf

# Should show:
# [include]
# files = /etc/supervisord.d/*.ini
```

---

### Issue: Programs show "FATAL" or "BACKOFF"

**Cause:** Program failed to start, usually due to wrong paths or missing dependencies.

**Fix:**
```bash
# Check error logs
sudo supervisorctl -c /etc/supervisord.conf tail xshows-gunicorn stderr

# Or check log files directly
sudo tail -50 /var/log/xshows/gunicorn-error.log

# Common fixes:
# 1. Verify virtual environment exists
ls -la /var/www/xshows/venv/bin/gunicorn

# 2. Verify working directory exists
ls -la /var/www/xshows

# 3. Test command manually
cd /var/www/xshows
source venv/bin/activate
gunicorn xshows.wsgi:application --bind 127.0.0.1:8000
```

---

### Issue: Supervisor won't start after reboot

**Cause:** Service not enabled or dependencies missing.

**Fix:**
```bash
# Enable service
sudo systemctl enable supervisord

# Check service status
sudo systemctl status supervisord

# View boot logs
sudo journalctl -u supervisord --boot
```

---

### Issue: Changes to config not taking effect

**Cause:** Forgot to reload supervisor.

**Fix:**
```bash
# After editing /etc/supervisord.d/xshows.ini
sudo supervisorctl -c /etc/supervisord.conf reread
sudo supervisorctl -c /etc/supervisord.conf update
sudo supervisorctl -c /etc/supervisord.conf restart xshows:*
```

---

## Best Practices

1. **Always use full paths** in program commands (no relative paths)
2. **Use separate log files** for stdout and stderr
3. **Set log rotation** to prevent disk space issues
4. **Use stopasgroup=true** for Celery to properly kill child processes
5. **Add environment variables** if needed (DATABASE_URL, etc.)
6. **Test commands manually** before adding to supervisor
7. **Check logs first** when troubleshooting

---

## File Locations Reference

| Item | Path |
|------|------|
| Main config | `/etc/supervisord.conf` |
| Program configs | `/etc/supervisord.d/*.ini` |
| Socket file | `/tmp/supervisord.sock` |
| PID file | `/tmp/supervisord.pid` |
| Main log | `/var/log/supervisord.log` |
| App logs | `/var/log/xshows/*.log` |
| Systemd service | `/etc/systemd/system/supervisord.service` |
| supervisord binary | `/usr/local/bin/supervisord` |
| supervisorctl binary | `/usr/local/bin/supervisorctl` |

---

## Quick Reference Commands

```bash
# Status check
sudo supervisorctl -c /etc/supervisord.conf status

# Restart all xshows services
sudo supervisorctl -c /etc/supervisord.conf restart xshows:*

# View logs
sudo tail -f /var/log/xshows/gunicorn.log

# After config changes
sudo supervisorctl -c /etc/supervisord.conf reread
sudo supervisorctl -c /etc/supervisord.conf update

# Restart supervisor service
sudo systemctl restart supervisord
```

---

**Created:** 2025-10-07
**For:** Amazon Linux 2023 EC2 instances
**Project:** XShows Django Application
