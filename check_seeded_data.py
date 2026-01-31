"""
Check where the seeded tokens are
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from django.utils import timezone
from queueapp.models import Token, Counter, Queue

today = timezone.now().date()

# Check all completed tokens today
all_completed = Token.objects.filter(
    status='completed',
    service_ended_at__date=today
).count()

print(f"Total completed tokens today: {all_completed}")
print()

# Check which queues have tokens
all_queues = Queue.objects.filter(is_active=True)
for queue in all_queues:
    completed = queue.tokens.filter(
        status='completed',
        service_ended_at__date=today
    ).count()
    if completed > 0:
        print(f"Queue '{queue.service_type}': {completed} completed tokens")

print()

# Check counter assignments
counters = Counter.objects.all()
for counter in counters:
    queues = counter.queues.all()
    print(f"Counter {counter.counter_id}: {list(queues.values_list('service_type', flat=True))}")
    
    completed = Token.objects.filter(
        queue__in=queues,
        status='completed',
        service_ended_at__date=today
    ).count()
    print(f"  → {completed} completed tokens")
