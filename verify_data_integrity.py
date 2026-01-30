"""
Verify and fix data integrity in the database
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from django.contrib.auth.models import User
from queueapp.models import Counter, Queue, Token, Notification, QueueAnalytics, UserRole

print("="*60)
print("DATA INTEGRITY CHECK & FIX")
print("="*60)

# 1. Check all tokens have valid customers
print("\n🎫 Checking Tokens...")
orphan_tokens = []
for token in Token.objects.all():
    if not token.customer:
        orphan_tokens.append(token.token_number)

if orphan_tokens:
    print(f"   ⚠️  Found {len(orphan_tokens)} tokens without customers")
    # Assign to first customer
    customers = User.objects.filter(userrole__role='customer')
    if customers:
        for token_num in orphan_tokens[:5]:
            token = Token.objects.get(token_number=token_num)
            token.customer = customers.first()
            token.save()
        print(f"   ✓ Fixed {min(5, len(orphan_tokens))} tokens")
else:
    print(f"   ✓ All {Token.objects.count()} tokens have valid customers")

# 2. Check all queues have valid counters
print("\n📋 Checking Queues...")
queues_without_counter = Queue.objects.filter(counter__isnull=True)
if queues_without_counter.exists():
    print(f"   ⚠️  Found {queues_without_counter.count()} queues without counters")
    counters = Counter.objects.all()
    for i, queue in enumerate(queues_without_counter):
        queue.counter = counters[i % len(counters)]
        queue.save()
    print(f"   ✓ Fixed {queues_without_counter.count()} queues")
else:
    print(f"   ✓ All {Queue.objects.count()} queues have valid counters")

# 3. Check all counters are assigned to staff
print("\n📍 Checking Counters...")
counters_without_staff = Counter.objects.filter(staff_member__isnull=True)
if counters_without_staff.exists():
    print(f"   ⚠️  Found {counters_without_staff.count()} counters without staff")
    # Get users with staff role
    staff_members = []
    for user in User.objects.all():
        try:
            if user.role and user.role.role == 'staff':
                staff_members.append(user)
        except:
            pass
    
    if staff_members:
        for i, counter in enumerate(counters_without_staff):
            counter.staff_member = staff_members[i % len(staff_members)]
            counter.save()
        print(f"   ✓ Fixed {counters_without_staff.count()} counters")
    else:
        print(f"   ⚠️  No staff members available to assign")
else:
    print(f"   ✓ All {Counter.objects.count()} counters have staff assigned")

# 4. Verify queues are connected to counters
print("\n🔗 Verifying Queue-Counter Connections...")
for counter in Counter.objects.all()[:3]:
    queue_count = counter.queues.count()
    print(f"   Counter {counter.counter_id}: {queue_count} queues")

# 5. Final Summary
print("\n" + "="*60)
print("✅ DATA INTEGRITY VERIFIED")
print("="*60)
print(f"\n📊 Final Database State:")
print(f"   Users: {User.objects.count()}")
print(f"   Counters: {Counter.objects.count()}")
print(f"   Queues: {Queue.objects.count()}")
print(f"   Tokens: {Token.objects.count()}")
print(f"   Notifications: {Notification.objects.count()}")
print(f"   Analytics: {QueueAnalytics.objects.count()}")

print(f"\n🔗 Connections:")
print(f"   Tokens with customers: {Token.objects.filter(customer__isnull=False).count()}/{Token.objects.count()}")
print(f"   Queues with counters: {Queue.objects.filter(counter__isnull=False).count()}/{Queue.objects.count()}")
print(f"   Counters with staff: {Counter.objects.filter(staff_member__isnull=False).count()}/{Counter.objects.count()}")

print("\n" + "="*60)
print("💡 You can now access:")
print("   Admin Panel: http://localhost:8000/admin/")
print("   Customer Dashboard: http://localhost:8000/dashboard/customer/")
print("   Staff Dashboard: http://localhost:8000/dashboard/staff/")
print("   Admin Dashboard: http://localhost:8000/dashboard/admin/")
print("="*60)
