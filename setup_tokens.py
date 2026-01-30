#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
sys.path.insert(0, r'c:\Users\priya\OneDrive\Documents\EY_4.0_sphn\projectey')
django.setup()

from queueapp.models import Counter, Queue, Token
from django.contrib.auth.models import User
from django.utils import timezone

print("Setting up counter and queue...")

# Create a counter
counter, counter_created = Counter.objects.get_or_create(
    counter_id='C001',
    defaults={
        'name': 'Counter 1',
        'description': 'Main counter',
        'status': 'active',
        'is_active': True,
        'is_online': True
    }
)
print(f"✓ Counter {counter.counter_id} ready")

# Create a queue
queue, queue_created = Queue.objects.get_or_create(
    queue_id='Q001',
    counter=counter,
    defaults={
        'service_type': 'general',
        'is_active': True,
        'average_service_time': 5
    }
)
print(f"✓ Queue {queue.queue_id} ready")

# Get customer1
try:
    customer = User.objects.get(username='customer1')
    print(f"✓ Found user: {customer.username}")
except User.DoesNotExist:
    print("✗ User 'customer1' not found!")
    sys.exit(1)

# Delete existing tokens for customer1 (optional - to avoid duplicates)
existing_tokens = Token.objects.filter(customer=customer)
existing_count = existing_tokens.count()

# Create 5 new tokens
print(f"\nCreating 5 tokens for {customer.username}...")
created_tokens = []
for i in range(5):
    token_number = f"TOK-{customer.username.upper()}-{timezone.now().strftime('%Y%m%d')}-{i+1:03d}"
    token = Token.objects.create(
        token_number=token_number,
        queue=queue,
        customer=customer,
        user=customer,
        status='generated',
        priority=1
    )
    created_tokens.append(token)
    print(f"  {i+1}. {token.token_number}")

# Verify
final_tokens = Token.objects.filter(customer=customer).count()
print(f"\n✓ Successfully added 5 tokens to {customer.username}")
print(f"  Total tokens for customer1: {final_tokens}")
