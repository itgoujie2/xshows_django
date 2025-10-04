"""
Test script for subscription and nudity detection system
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xshows.settings')
django.setup()

from models_app.models import WebcamModel, Subscription
from users.models import User

print("=" * 80)
print("SUBSCRIPTION & NUDITY DETECTION TEST")
print("=" * 80)

# 1. Create or get test user
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
        'first_name': 'Test',
        'last_name': 'User',
    }
)
if created:
    user.set_password('password123')
    user.save()
    print(f"\n✅ Created test user: {user.username}")
else:
    print(f"\n✅ Using existing test user: {user.username}")

# 2. Get some online models
online_models = WebcamModel.objects.filter(is_online=True)
count = online_models.count()
print(f"\n📊 Found {count} online models")

# 3. Create subscription to first model
if count > 0:
    model = online_models[0]

    subscription, created = Subscription.objects.get_or_create(
        user=user,
        model=model,
        defaults={
            'is_active': True,
            'notification_method': 'email'
        }
    )

    if created:
        print(f"\n✅ Created subscription: {user.username} → {model.display_name}")
    else:
        print(f"\n✅ Subscription already exists: {user.username} → {model.display_name}")

    print(f"   Model: {model.display_name}")
    print(f"   Username: {model.user_name}")
    print(f"   Image URL: {model.image[:80]}...")
    print(f"   Is Online: {model.is_online}")
    print(f"   Source: {model.source}")

    # 4. Test nudity detection
    print(f"\n🔍 Testing nudity detection for {model.display_name}...")

    from models_app.nudity_detector import NudityDetectionService
    detector = NudityDetectionService()

    is_naked, confidence, image_hash = detector.check_model_image(model.image)

    print(f"\n📊 Nudity Detection Results:")
    print(f"   Is Naked: {is_naked}")
    print(f"   Confidence: {confidence * 100:.1f}%" if confidence else "   Confidence: N/A")
    print(f"   Image Hash: {image_hash}")

    # Update model
    model.is_naked = is_naked
    model.nudity_confidence = confidence
    model.nudity_image_hash = image_hash
    model.save()

    print(f"\n✅ Model updated in database")

    # 5. Check subscriptions
    total_subs = Subscription.objects.filter(is_active=True).count()
    print(f"\n📊 Statistics:")
    print(f"   Total active subscriptions: {total_subs}")
    print(f"   Subscribed models: {Subscription.objects.filter(is_active=True).values('model').distinct().count()}")

    # 6. Show what will happen next
    print(f"\n🔔 What happens next:")
    print(f"   1. Every 5 minutes, scraping runs automatically")
    print(f"   2. After scraping, nudity detection runs for subscribed models")
    print(f"   3. If model is naked, notification email will be sent to {user.email}")
    print(f"   4. Rate limit: Max 1 email per model per 30 minutes")

    if is_naked:
        print(f"\n🔥 {model.display_name} is currently NAKED!")
        print(f"   Subscribers will be notified on the next check (every 5 min)")
    else:
        print(f"\n😊 {model.display_name} is not showing explicit nudity right now")
        print(f"   Subscribers will be notified when nudity is detected")

else:
    print("\n❌ No online models found. Run scraping first.")

print("\n" + "=" * 80)
print("To manually trigger nudity check:")
print("=" * 80)
print("""
cd ~/Downloads/xshows_django
source venv/bin/activate
python manage.py shell

from models_app.tasks import check_subscribed_models_for_nudity
check_subscribed_models_for_nudity.delay()
""")

print("\n" + "=" * 80)
print("✅ TEST COMPLETE")
print("=" * 80)
