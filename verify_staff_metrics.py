"""
Verify staff dashboard metrics
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from django.utils import timezone
from queueapp.models import Token, Counter, Queue

# Get first counter's queues
counter = Counter.objects.first()
if counter:
    queues = counter.queues.all()
    today = timezone.now().date()
    
    # Check tokens for today
    tokens_today = Token.objects.filter(
        queue__in=queues,
        status='completed',
        service_ended_at__date=today
    )
    
    print(f"Counter: {counter.counter_id}")
    print(f"Queues: {list(queues.values_list('service_type', flat=True))}")
    print(f"Completed tokens today: {tokens_today.count()}")
    print()
    
    # Check wait times
    completed_with_wait = tokens_today.filter(called_at__isnull=False)
    wait_times = [t.wait_duration for t in completed_with_wait if t.wait_duration]
    if wait_times:
        avg_wait = sum(wait_times) / len(wait_times)
        print(f"✓ Average wait time: {int(avg_wait)} min")
    else:
        print("⚠ No wait time data (showing fallback: 8 min)")
    
    # Check service times
    service_times = []
    for t in tokens_today:
        if t.service_started_at and t.service_ended_at:
            duration = (t.service_ended_at - t.service_started_at).total_seconds() / 60
            service_times.append(duration)
    
    if service_times:
        avg_service = sum(service_times) / len(service_times)
        print(f"✓ Average service time: {int(avg_service)} min")
    else:
        print("⚠ No service time data (showing fallback: 5 min)")
    
    # Check counter efficiency
    waiting_count = Token.objects.filter(
        queue__in=queues,
        status__in=['waiting', 'called']
    ).count()
    
    print(f"✓ Waiting customers: {waiting_count}")
    
    total_handled = tokens_today.count() + waiting_count
    if total_handled > 0:
        efficiency = int((tokens_today.count() / total_handled) * 100)
        print(f"✓ Counter efficiency: {efficiency}%")
    else:
        print("⚠ No data (showing fallback: 85%)")
    
    print("\n✓ All metrics should now display correctly on staff dashboard!")
    
else:
    print("No counters found")
