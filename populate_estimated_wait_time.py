#!/usr/bin/env python
"""Populate estimated_wait_time for all tokens"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from queueapp.models import Token, Queue
from django.utils import timezone
import random

# For each queue, calculate average service time
for queue in Queue.objects.all():
    # Get completed tokens in this queue
    completed = queue.tokens.filter(
        status='completed',
        service_started_at__isnull=False,
        service_ended_at__isnull=False
    )
    
    if completed.exists():
        avg_service_time = sum([
            (t.service_ended_at - t.service_started_at).total_seconds() / 60
            for t in completed
        ]) / completed.count()
    else:
        avg_service_time = 5  # Default 5 minutes
    
    # Get waiting tokens count at time of generation (use current waiting as proxy)
    current_waiting = queue.tokens.filter(
        status__in=['waiting', 'called']
    ).count()
    
    print(f"Queue {queue.service_type}: avg_service={avg_service_time:.1f}min, currently_waiting={current_waiting}")
    
    # Update all tokens in this queue
    for token in queue.tokens.all():
        if token.estimated_wait_time is None:
            # Estimate: (tokens_in_queue_before + 1) * avg_service_time
            tokens_before = queue.tokens.filter(
                generated_at__lt=token.generated_at,
                status__in=['waiting', 'called', 'being_served']
            ).count()
            
            estimated = max(1, int((tokens_before + 1) * avg_service_time))
            token.estimated_wait_time = estimated
            token.save()

print("\nUpdated all tokens with estimated_wait_time")

# Verify by checking a sample
sample = Token.objects.filter(estimated_wait_time__isnull=False).first()
if sample:
    print(f"\nSample Token {sample.token_number}:")
    print(f"  Estimated wait: {sample.estimated_wait_time} min")
    print(f"  Actual wait: {sample.wait_duration} min")
    if sample.wait_duration and sample.estimated_wait_time:
        time_saved = sample.estimated_wait_time - sample.wait_duration
        print(f"  Time saved: {time_saved} min")
