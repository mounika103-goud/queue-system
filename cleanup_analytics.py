"""
Clear duplicate QueueAnalytics records to fix UNIQUE constraint issue
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from queueapp.models import QueueAnalytics

print("="*60)
print("CLEARING DUPLICATE QUEUEANALYTICS RECORDS")
print("="*60)

# Get all analytics
all_analytics = QueueAnalytics.objects.all()
print(f"\nTotal records: {all_analytics.count()}")

# Group by (date, queue) and find duplicates
from django.db.models import Count

duplicates = QueueAnalytics.objects.values('date', 'queue').annotate(
    count=Count('id')
).filter(count__gt=1)

print(f"Duplicate (date, queue) combinations: {duplicates.count()}")

# Delete all but the first record in each group
deleted_count = 0
for dup in duplicates:
    records = QueueAnalytics.objects.filter(
        date=dup['date'],
        queue_id=dup['queue']
    ).order_by('id')[1:]  # Keep first, delete rest
    
    deleted_count += records.count()
    records.delete()
    print(f"  ✓ Cleaned {records.count()} duplicates for date={dup['date']}, queue_id={dup['queue']}")

print(f"\n✓ Deleted {deleted_count} duplicate records")
print(f"✓ Remaining records: {QueueAnalytics.objects.count()}")

print("\n" + "="*60)
print("✅ CLEANUP COMPLETE")
print("="*60)
print("\n💡 You can now add new QueueAnalytics records without issues!")
