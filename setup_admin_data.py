"""
Setup script to ensure admin user has all permissions and data is visible
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from queueapp.models import Counter, Queue, Token, Notification, QueueAnalytics, UserRole

print("="*60)
print("SETUP ADMIN AND DATA VISIBILITY")
print("="*60)

# 1. Get or create admin user
admin_user = User.objects.filter(username='admin').first()
if admin_user:
    print(f"\n✅ Admin user found: {admin_user.username}")
    
    # Make sure admin is superuser and staff
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()
    print("   ✓ Superuser permissions verified")
    
    # Ensure admin role
    admin_role, created = UserRole.objects.get_or_create(
        user=admin_user,
        defaults={'role': 'admin', 'is_active': True}
    )
    if created:
        print("   ✓ Admin role created")
    else:
        admin_role.role = 'admin'
        admin_role.is_active = True
        admin_role.save()
        print("   ✓ Admin role updated")
else:
    print("\n❌ Admin user not found!")
    print("   Creating admin user...")
    admin_user = User.objects.create_superuser(
        username='admin',
        email='admin@bank.com',
        password='admin123'
    )
    UserRole.objects.create(user=admin_user, role='admin', is_active=True)
    print("   ✓ Admin user created")

# 2. Check data visibility
print("\n📊 Data Summary:")
print(f"   Counters: {Counter.objects.count()}")
print(f"   Queues: {Queue.objects.count()}")
print(f"   Tokens: {Token.objects.count()}")
print(f"   Notifications: {Notification.objects.count()}")
print(f"   Analytics: {QueueAnalytics.objects.count()}")

# 3. Verify data is connected properly
print("\n🔗 Data Connections:")

# Check counters have queues
for counter in Counter.objects.all()[:2]:
    queue_count = counter.queues.count()
    print(f"   Counter {counter.counter_id}: {queue_count} queues")

# Check queues have tokens
for queue in Queue.objects.all()[:2]:
    token_count = queue.tokens.count()
    print(f"   Queue {queue.queue_id}: {token_count} tokens")

# 4. Grant all permissions to admin
print("\n🔐 Granting Permissions:")
admin_user.user_permissions.clear()
admin_user.groups.clear()

# Add all app permissions
all_permissions = Permission.objects.filter(content_type__app_label='queueapp')
admin_user.user_permissions.add(*all_permissions)
print(f"   ✓ Added {all_permissions.count()} app permissions")

# Add auth permissions
auth_permissions = Permission.objects.filter(content_type__app_label='auth')
admin_user.user_permissions.add(*auth_permissions)
print(f"   ✓ Added auth permissions")

admin_user.save()

print("\n" + "="*60)
print("✅ ADMIN SETUP COMPLETE")
print("="*60)
print("\n📍 Admin Access:")
print("   URL: http://localhost:8000/admin/")
print("   Username: admin")
print("   Password: admin123")
print("\n💡 All data should now be visible in the admin panel!")
print("="*60)
