"""
Clean up duplicate counter assignments
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from queueapp.models import Counter
from collections import defaultdict

print("="*60)
print("CLEANUP: Duplicate Counter Assignments")
print("="*60)

# Find and clean duplicates
staff_counters = defaultdict(list)

for counter in Counter.objects.filter(staff_member__isnull=False):
    staff_counters[counter.staff_member].append(counter)

cleaned = 0
for staff, counters in staff_counters.items():
    if len(counters) > 1:
        print(f"\nUser: {staff.username}")
        print(f"Assigned to {len(counters)} counters:")
        
        # Keep the first, unassign the rest
        for i, counter in enumerate(counters):
            if i == 0:
                print(f"  ✓ KEEP: Counter {counter.counter_id}")
            else:
                print(f"  ✗ REMOVE: Counter {counter.counter_id}")
                counter.staff_member = None
                counter.save()
                cleaned += 1

print(f"\n{'='*60}")
print(f"✅ Cleaned up {cleaned} duplicate assignments")
print(f"{'='*60}")
