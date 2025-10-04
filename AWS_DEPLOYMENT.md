# AWS EC2 Deployment Guide - Amazon Linux 2023

## Architecture Overview

```
EC2 Instance (Amazon Linux 2023)
├── Nginx (web server - reverse proxy)
├── Gunicorn (Django WSGI server)
├── Supervisor (manages Celery workers + Gunicorn)
├── Redis (Celery broker)
├── MySQL (database - on same instance or RDS)
└── NudeNet AI (nudity detection - optimized for t3.small)
```

## Cost Estimate

- **EC2 t3.small**: ~$15/month (2 vCPU, 2GB RAM) - **Recommended for NudeNet**
- **RDS MySQL db.t3.micro**: ~$15/month (optional, can use local MySQL)
- **ElastiCache Redis** (optional): ~$13/month OR free (install on EC2)
- **Total**: ~$15-45/month

**Recommended**: t3.small with local MySQL/Redis (~$15/month)

---

## Step 1: Launch EC2 Instance

### 1.1 Create EC2 Instance

1. Go to AWS Console → EC2 → Launch Instance
2. **Name**: `xshows-production`
3. **AMI**: Amazon Linux 2023 AMI
4. **Instance type**: t3.small (2GB RAM required for NudeNet)
5. **Key pair**: Create new or use existing (download .pem file)
6. **Security group**: Create with these rules:
   - SSH (22) - Your IP only
   - HTTP (80) - 0.0.0.0/0
   - HTTPS (443) - 0.0.0.0/0
7. **Storage**: 30 GB gp3 (larger for swap space)
8. Click **Launch Instance**

### 1.2 Connect to Instance

```bash
# On your local machine
chmod 400 your-key.pem
ssh -i your-key.pem ec2-user@your-ec2-public-ip
```

---

## Step 2: Install Dependencies on EC2

```bash
# Update system (use dnf for Amazon Linux 2023)
sudo dnf update -y

# Install Python 3.11 and development tools
sudo dnf install -y python3.11 python3.11-pip python3.11-devel gcc git

# Install MySQL 8.0
sudo dnf install -y mariadb105-server mariadb105-devel

# Install Redis
sudo dnf install -y redis6

# Install Nginx
sudo dnf install -y nginx

# Install Supervisor
sudo dnf install -y supervisor

# Start and enable services
sudo systemctl start mariadb redis6 nginx supervisord
sudo systemctl enable mariadb redis6 nginx supervisord

# Secure MySQL
sudo mysql_secure_installation
# Answer: Y for all prompts, set a strong root password
```

---

## Step 3: Set Up Project

### 3.1 Setup Swap Space (CRITICAL for t3.small + NudeNet!)

```bash
# Upload swap setup script
# On your local machine:
scp -i your-key.pem setup_swap.sh ec2-user@your-ec2-ip:~/

# On EC2:
chmod +x ~/setup_swap.sh
sudo ~/setup_swap.sh

# Verify swap is active
free -h
# Should show 4GB swap
```

### 3.2 Clone Repository

```bash
# Create directory
sudo mkdir -p /var/www
sudo chown ec2-user:ec2-user /var/www
cd /var/www

# Clone your repository (replace with your repo URL)
git clone https://github.com/yourusername/xshows_django.git xshows
cd xshows

# Or upload via SCP from local machine:
# scp -i your-key.pem -r ~/Downloads/xshows_django/* ec2-user@your-ec2-ip:/var/www/xshows/
```

### 3.3 Set Up Virtual Environment

```bash
cd /var/www/xshows
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn nudenet
```

### 3.4 Configure Environment Variables

```bash
# Copy optimized t3.small config
cp .env.t3small .env

# Edit with your values
nano .env
```

Update these values:
```ini
# Django
SECRET_KEY=your-production-secret-key-generate-new-one
DEBUG=False
ALLOWED_HOSTS=your-domain.com,your-ec2-public-ip

# Database (local MySQL)
DB_HOST=127.0.0.1
DB_DATABASE=xshows
DB_USERNAME=xshows_user
DB_PASSWORD=your-secure-password

# Redis (local)
CELERY_BROKER_URL=redis://127.0.0.1:6379/0
CELERY_RESULT_BACKEND=redis://127.0.0.1:6379/0
REDIS_HOST=redis://127.0.0.1:6379/1

# Memory optimization for t3.small (already set in .env.t3small)
CELERY_WORKER_CONCURRENCY=2
MAX_NUDITY_CHECKS_PER_RUN=20

# Site URL
SITE_URL=https://your-domain.com

# Email
MAIL_HOST=smtp.gmail.com
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
```

**Generate Secret Key:**
```bash
python3.11 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 3.5 Database Setup

**Using local MySQL (recommended for t3.small to save costs):**

```bash
# Create database and user
sudo mysql -u root -p
```

```sql
CREATE DATABASE xshows CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'xshows_user'@'localhost' IDENTIFIED BY 'your-strong-password';
GRANT ALL PRIVILEGES ON xshows.* TO 'xshows_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

**Run migrations:**
```bash
cd /var/www/xshows
source venv/bin/activate
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

**Test server:**
```bash
python manage.py runserver 0.0.0.0:8000
# Visit http://your-ec2-ip:8000 (temporarily open port 8000 in security group if needed)
# Ctrl+C to stop
```

---

## Step 4: Configure Supervisor

### 4.1 Create Log Directory

```bash
sudo mkdir -p /var/log/xshows
sudo chown ec2-user:ec2-user /var/log/xshows
```

### 4.2 Create Supervisor Configuration

```bash
sudo nano /etc/supervisord.d/xshows.ini
```

**Content (optimized for t3.small):**
```ini
[group:xshows]
programs=xshows-gunicorn,xshows-celery-worker,xshows-celery-beat

[program:xshows-gunicorn]
command=/var/www/xshows/venv/bin/gunicorn xshows.wsgi:application --bind 127.0.0.1:8000 --workers 2 --timeout 120
directory=/var/www/xshows
user=ec2-user
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/xshows/gunicorn.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
environment=PATH="/var/www/xshows/venv/bin"

[program:xshows-celery-worker]
command=/var/www/xshows/venv/bin/celery -A xshows worker -l info --concurrency=2 --max-tasks-per-child=50
directory=/var/www/xshows
user=ec2-user
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/xshows/celery-worker.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
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
redirect_stderr=true
stdout_logfile=/var/log/xshows/celery-beat.log
stdout_logfile_maxbytes=10MB
stdout_logfile_backups=3
environment=PATH="/var/www/xshows/venv/bin"
```

### 4.3 Start Supervisor

```bash
# Reload Supervisor configuration
sudo supervisorctl reread
sudo supervisorctl update

# Start all processes
sudo supervisorctl start xshows:*

# Check status
sudo supervisorctl status
```

**Expected output:**
```
xshows:xshows-celery-beat     RUNNING   pid 1234, uptime 0:00:05
xshows:xshows-celery-worker   RUNNING   pid 1235, uptime 0:00:05
xshows:xshows-gunicorn        RUNNING   pid 1236, uptime 0:00:05
```

---

## Step 5: Configure Nginx

### 5.1 Create Nginx Configuration

```bash
sudo nano /etc/nginx/conf.d/xshows.conf
```

**Content:**
```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;  # Or your EC2 IP
    client_max_body_size 20M;

    # Static files
    location /static/ {
        alias /var/www/xshows/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias /var/www/xshows/media/;
        expires 7d;
    }

    # Django application
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_read_timeout 300s;
    }
}
```

### 5.2 Configure Nginx

```bash
# Test configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx

# Verify it's running
sudo systemctl status nginx
```

---

## Step 6: Configure HTTPS (Optional but Recommended)

### 6.1 Install Certbot

```bash
# Install EPEL and certbot
sudo dnf install -y certbot python3-certbot-nginx
```

### 6.2 Get SSL Certificate

```bash
# Make sure your domain points to EC2 IP first
sudo certbot --nginx -d your-domain.com -d www.your-domain.com

# Follow prompts:
# 1. Enter email
# 2. Agree to terms
# 3. Choose redirect HTTP to HTTPS (recommended)
```

**Test auto-renewal:**
```bash
sudo certbot renew --dry-run
```

---

## Step 7: Monitoring & Management

### Common Supervisor Commands

```bash
# Check status
sudo supervisorctl status

# Start all
sudo supervisorctl start xshows:*

# Stop all
sudo supervisorctl stop xshows:*

# Restart all
sudo supervisorctl restart xshows:*

# Restart specific service
sudo supervisorctl restart xshows:xshows-gunicorn

# View logs
sudo tail -f /var/log/xshows/gunicorn.log
sudo tail -f /var/log/xshows/celery-worker.log
sudo tail -f /var/log/xshows/celery-beat.log

# Reload configuration after changes
sudo supervisorctl reread
sudo supervisorctl update
```

### Application Updates

```bash
# SSH to EC2
ssh -i your-key.pem ec2-user@your-ec2-ip

# Pull latest code
cd /var/www/xshows
git pull

# Activate venv and update
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput

# Restart services
sudo supervisorctl restart xshows:*
```

---

## Step 8: Security Hardening

### 8.1 Firewall (firewalld)

```bash
# Amazon Linux 2023 uses firewalld
sudo systemctl start firewalld
sudo systemctl enable firewalld

# Allow HTTP and HTTPS
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https

# Reload firewall
sudo firewall-cmd --reload

# Check status
sudo firewall-cmd --list-all
```

### 8.2 Fail2Ban (Prevent brute force)

```bash
sudo dnf install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

### 8.3 Django Settings

In `settings.py`:
```python
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com', 'your-ec2-ip']
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
```

---

## Step 9: Backup Strategy

### Database Backups

```bash
# Create backup script
nano ~/backup.sh
```

```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/var/backups/xshows
mkdir -p $BACKUP_DIR

# Backup database
mysqldump -u xshows_user -p'your-password' xshows | gzip > $BACKUP_DIR/db_$DATE.sql.gz

# Upload to S3 (optional - requires AWS CLI configured)
# aws s3 cp $BACKUP_DIR/db_$DATE.sql.gz s3://your-backup-bucket/

# Keep only last 7 days
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +7 -delete
```

```bash
chmod +x ~/backup.sh

# Add to crontab (daily at 2 AM)
crontab -e
# Add: 0 2 * * * /home/ec2-user/backup.sh
```

---

## Troubleshooting

### Check if services are running

```bash
sudo supervisorctl status
sudo systemctl status nginx
sudo systemctl status redis
```

### Check logs

```bash
# Application errors
sudo tail -f /var/log/xshows/gunicorn.log

# Celery worker
sudo tail -f /var/log/xshows/celery-worker.log

# Nginx errors
sudo tail -f /var/log/nginx/error.log

# System logs
sudo journalctl -u supervisor -f
```

### Common Issues

**502 Bad Gateway:**
- Gunicorn not running: `sudo supervisorctl restart xshows:xshows-gunicorn`
- Wrong socket/port in Nginx config

**Static files not loading:**
```bash
python manage.py collectstatic --noinput
sudo systemctl restart nginx
```

**Database connection issues:**
- Check RDS security group allows EC2 security group
- Test connection: `mysql -h endpoint -u admin -p`

**Celery tasks not running:**
```bash
# Check Redis
redis-cli ping  # Should return PONG

# Check Celery logs
sudo tail -f /var/log/xshows/celery-worker.log
```

---

## Scaling Tips

### Vertical Scaling (Bigger Instance)
1. Stop EC2 instance
2. Change instance type (t3.small → t3.medium)
3. Start instance

### Horizontal Scaling (Load Balancer)
1. Create AMI from current instance
2. Launch multiple instances from AMI
3. Create Application Load Balancer
4. Point domain to ALB

### Database Scaling
1. Upgrade RDS instance size
2. Enable Multi-AZ for high availability
3. Add read replicas for heavy read loads

---

## Monitoring (Optional)

### CloudWatch Alarms
- CPU utilization > 80%
- Disk space < 20%
- Memory usage > 90%

### Application Monitoring
- Install Sentry for error tracking
- Use AWS CloudWatch Logs for centralized logging

---

## Monthly Maintenance Checklist

- [ ] Check disk space: `df -h`
- [ ] Check memory usage: `free -h` (verify swap not overused)
- [ ] Check logs for errors
- [ ] Review database backups
- [ ] Update packages: `sudo dnf update -y`
- [ ] Check SSL certificate expiry: `sudo certbot renew`
- [ ] Review CloudWatch metrics
- [ ] Test backup restoration
- [ ] Monitor NudeNet memory usage in logs

---

## Contact & Support

- AWS Documentation: https://docs.aws.amazon.com/
- Django Deployment: https://docs.djangoproject.com/en/stable/howto/deployment/
- Supervisor Docs: http://supervisord.org/
- Nginx Docs: https://nginx.org/en/docs/

---

**Deployment Date**: _____________
**Deployed By**: _____________
**Domain**: _____________
**EC2 IP**: _____________

---

## t3.small Memory Optimization Summary

### What Was Optimized

1. **Swap Space**: 4GB swap file prevents OOM crashes
2. **Lazy Loading**: NudeNet model loads only when first needed
3. **Limited Concurrency**: Max 2 Celery tasks run simultaneously
4. **Batching**: Max 20 nudity checks per 5-minute cycle
5. **Worker Recycling**: Celery worker restarts after 50 tasks to prevent memory leaks
6. **Gunicorn Workers**: Limited to 2 workers instead of default 3

### Memory Breakdown

| Service | Memory Usage |
|---------|--------------|
| System/OS | ~200 MB |
| MySQL | ~200 MB |
| Redis | ~50 MB |
| Nginx | ~20 MB |
| Gunicorn (2 workers) | ~200 MB |
| Celery Worker (idle) | ~150 MB |
| Celery Beat | ~100 MB |
| NudeNet (when active) | ~800-1000 MB |
| **Total (peak)** | **~1.7-1.9 GB** |
| **Swap Buffer** | **4 GB available** |

### Performance Expectations

- **Handles**: 50-100 active subscriptions
- **Nudity Checks**: ~240 per hour (20 every 5 min)
- **Response Time**: 1-2 seconds (web)
- **Swap Usage**: Occasional during NudeNet processing
- **Uptime**: Stable with optimizations

### When to Upgrade to t3.medium

Upgrade if you experience:
- Swap usage consistently > 2GB
- More than 100 active subscriptions
- Frequent OOM errors despite swap
- Slow response times (>3 sec)
- Need more than 240 nudity checks/hour

**t3.medium** (4GB RAM, $30/mo): Handles 500+ subscriptions, no swap needed
