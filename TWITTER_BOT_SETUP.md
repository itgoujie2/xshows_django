# 🐦 Twitter Bot Setup Guide

## Overview
The Twitter bot automatically tweets when popular models (500+ viewers) are detected as naked by the AI.

**Features:**
- ✅ Auto-tweets every 15 minutes
- ✅ Only tweets about popular models (500+ viewers)
- ✅ Rate limit: 1 tweet per model per hour
- ✅ Max 3 tweets per run (avoid spam)
- ✅ Includes viewer count, confidence, and affiliate link

---

## 🔑 Step 1: Create Twitter Developer Account

### 1.1 Sign Up for Twitter Developer Account
1. Go to https://developer.twitter.com/
2. Click "Sign up" or "Apply"
3. Log in with your Twitter account (@XShowsAlerts or create new)
4. Fill out the application form:
   - **Use case**: Building automation tools
   - **Description**: "Automated alerts for live webcam model notifications"
   - Check "Are you planning to analyze Twitter data": NO
   - Select "Making a bot"

### 1.2 Wait for Approval
- Usually approved within 1-24 hours
- Check your email for approval notification

### 1.3 Create a Project & App
1. Once approved, go to Developer Portal: https://developer.twitter.com/en/portal/dashboard
2. Click **"Create Project"**
   - Project name: `XShows Alerts`
   - Use case: `Making a bot`
   - Description: `Automated nudity alerts for webcam models`

3. Click **"Create App"**
   - App name: `XShows Bot` (must be unique)
   - Environment: `Production`

---

## 🔐 Step 2: Get API Keys

### 2.1 Get API Keys
1. In your app settings, go to **"Keys and tokens"** tab
2. Copy these credentials:
   - **API Key** (Consumer Key)
   - **API Key Secret** (Consumer Secret)

### 2.2 Generate Access Tokens
1. Scroll down to **"Authentication Tokens"**
2. Click **"Generate"** under **Access Token and Secret**
3. Copy:
   - **Access Token**
   - **Access Token Secret**

⚠️ **Important**: Save these credentials securely! You won't see them again.

---

## ⚙️ Step 3: Configure XShows

### 3.1 Update .env File
Open `/Users/jiegou/Downloads/xshows_django/.env` and update:

```ini
# Twitter API Configuration
TWITTER_API_KEY=your-actual-api-key-here
TWITTER_API_SECRET=your-actual-api-secret-here
TWITTER_ACCESS_TOKEN=your-actual-access-token-here
TWITTER_ACCESS_TOKEN_SECRET=your-actual-access-token-secret-here
```

### 3.2 Restart Services
```bash
cd ~/Downloads/xshows_django
source venv/bin/activate
supervisorctl -c supervisord.conf restart all
```

---

## 🧪 Step 4: Test the Bot

### 4.1 Mark Test Models as Popular
```bash
source venv/bin/activate
python manage.py shell
```

```python
from models_app.models import WebcamModel

# Find a naked model
model = WebcamModel.objects.filter(is_naked=True, is_online=True).first()

if model:
    # Mark as popular for testing
    model.is_popular = True
    model.save()
    print(f"✅ Marked {model.display_name} as popular")

    # Test tweet
    from models_app.twitter_bot import TwitterBot
    bot = TwitterBot()

    if bot.should_tweet_about_model(model):
        success = bot.post_tweet(model)
        if success:
            print(f"✅ Tweet posted successfully!")
        else:
            print("❌ Tweet failed")
    else:
        print("Model not eligible for tweeting")
else:
    print("No naked models found")
```

### 4.2 Check Twitter
Go to your Twitter account and verify the tweet was posted!

---

## 📋 How It Works

### Automated Flow (Every 15 Minutes):

1. **Update Popular Models** (every 10 minutes)
   - Checks all online models
   - Marks models with 500+ viewers as `is_popular=True`

2. **Tweet Popular Naked Models** (every 15 minutes)
   - Gets all models where:
     - `is_naked=True`
     - `is_online=True`
     - `is_popular=True`
   - For each model, checks:
     - Not tweeted in last hour
     - Confidence > 60%
   - Posts tweet with:
     - Model name
     - Viewer count
     - Confidence percentage
     - Affiliate link
   - Limits to 3 tweets per run

### Tweet Format Example:
```
🔴 LIVE & NAKED! 🔥

Bridget Jean is showing off right NOW!

👥 4,759 viewers watching
🔥 83% confidence
📍 CHATURBATE

Watch: https://chaturbate.com/in/?tour=yiMH&campaign=xvfw7&room=bridgetjean

#Chaturbate #LiveCam #NSFW
```

---

## 🎛️ Configuration Options

### Adjust Popularity Threshold
Edit `xshows/celery.py` line 43:
```python
'args': (500,),  # Change 500 to your desired viewer count
```

### Adjust Tweet Frequency
Edit `xshows/celery.py` line 49:
```python
'schedule': crontab(minute='*/15'),  # Change */15 to */30 for every 30 min
```

### Adjust Tweets Per Run
Edit `models_app/tasks.py` line 647:
```python
if tweeted_count >= 3:  # Change 3 to your desired max
```

### Adjust Hourly Rate Limit
Edit `models_app/twitter_bot.py` line 121:
```python
if time_since_last_tweet.total_seconds() < 3600:  # Change 3600 to seconds
```

---

## 📊 Monitoring

### Check Bot Status
```bash
source venv/bin/activate
python manage.py shell
```

```python
from models_app.models import WebcamModel

# Check popular models
popular = WebcamModel.objects.filter(is_popular=True, is_online=True)
print(f"Popular models: {popular.count()}")

# Check tweeted models
tweeted = WebcamModel.objects.filter(last_tweeted_at__isnull=False).order_by('-last_tweeted_at')[:10]
for m in tweeted:
    print(f"{m.display_name}: {m.tweet_count} tweets, last: {m.last_tweeted_at}")
```

### Check Celery Logs
```bash
tail -f logs/celery-worker.log | grep -i "twitter"
```

### View Scheduled Tasks
```bash
source venv/bin/activate
python manage.py shell
```

```python
from django_celery_beat.models import PeriodicTask

tasks = PeriodicTask.objects.filter(name__icontains='tweet')
for task in tasks:
    print(f"{task.name}: {task.enabled}, last run: {task.last_run_at}")
```

---

## 🚫 Troubleshooting

### Bot Not Tweeting?

**Check 1: Twitter API Keys**
```bash
python manage.py shell
```
```python
from django.conf import settings
print(f"API Key: {settings.TWITTER_API_KEY[:10]}...")
print(f"Enabled: {bool(settings.TWITTER_API_KEY)}")
```

**Check 2: Popular Models**
```python
from models_app.models import WebcamModel
count = WebcamModel.objects.filter(is_popular=True, is_naked=True, is_online=True).count()
print(f"Popular naked models: {count}")
```

**Check 3: Celery Running**
```bash
supervisorctl -c supervisord.conf status
```

**Check 4: Twitter Rate Limits**
- Twitter has rate limits: 300 tweets per 3 hours
- Our bot posts max 3 tweets per 15 minutes = 12/hour = safe

### Twitter API Errors?

**401 Unauthorized**
- Check API keys are correct in `.env`
- Regenerate access tokens if needed

**403 Forbidden**
- Your app may need elevated access
- Apply for Elevated Access in Twitter Developer Portal

**429 Rate Limit**
- You've hit Twitter's rate limit
- Wait 15 minutes and try again
- Reduce tweet frequency

---

## 📈 Best Practices

### 1. Quality Over Quantity
- Don't tweet too often (spam = ban)
- Focus on truly popular models (500+ viewers)
- Use engaging copy

### 2. Monitor Engagement
- Check which tweets get clicks
- Adjust model popularity threshold
- Test different tweet formats

### 3. Stay Compliant
- Don't violate Twitter's automation rules
- No misleading content
- Respect rate limits
- Include relevant hashtags

### 4. Grow Your Following
- Follow model accounts
- Retweet model announcements
- Engage with followers
- Use trending hashtags

---

## 🎯 Growth Tips

### Build Credibility
1. Tweet consistently (bot handles this)
2. Retweet popular cam models manually
3. Reply to follower questions
4. Pin your best-performing tweet

### Optimize Hashtags
- #Chaturbate (high volume)
- #LiveCam (medium volume)
- #NSFW (high reach but competitive)
- Model name hashtags
- Trending adult hashtags

### Cross-Promote
- Add Twitter link to website
- Mention Twitter in email notifications
- Create Discord bot that posts tweets

---

## 🔄 Next Steps

### Phase 1 (Week 1):
- ✅ Set up bot
- ✅ Test with 1-2 tweets
- Monitor performance
- Adjust thresholds

### Phase 2 (Week 2-4):
- Build to 100+ followers
- Optimize tweet times
- A/B test tweet formats
- Add model photos (if allowed)

### Phase 3 (Month 2+):
- 1,000+ followers
- Partner with models
- Sponsored tweets
- Premium alert tier

---

## 📝 Tweet Template Variations

You can edit `models_app/twitter_bot.py` line 42-60 to customize:

**Option 1: Short & Direct**
```python
tweet = f"🔴 {model.display_name} is LIVE & NAKED!\n👥 {viewers} watching\nWatch: {model.chat_url}"
```

**Option 2: Engagement Focus**
```python
tweet = f"She's live NOW! 🔥\n\n{model.display_name} just went nude with {viewers} viewers!\n\nDon't miss out 👇\n{model.chat_url}"
```

**Option 3: Urgency**
```python
tweet = f"⚡ ALERT ⚡\n\n{model.display_name} is naked RIGHT NOW!\n\n{viewers} people are already watching\n\nJoin: {model.chat_url}"
```

---

## 📚 Resources

- **Twitter API Docs**: https://developer.twitter.com/en/docs
- **Tweepy Docs**: https://docs.tweepy.org/
- **Twitter Automation Rules**: https://help.twitter.com/en/rules-and-policies/twitter-automation

---

**Last Updated**: 2025-10-03
**Status**: Ready to Deploy

**Questions?** Check the logs or create an issue!
