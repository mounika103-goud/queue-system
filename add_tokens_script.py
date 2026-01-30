import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from queueapp.models import Counter, Queue
from django.contrib.auth.models import User

# Create a counter if it doesn't exist
counter, created = Counter.objects.get_or_create(
    counter_id='C001',
    defaults={
        'name': 'Counter 1',
        'description': 'Main counter',
        'status': 'active',
        'is_active': True,
        'is_online': True
    }
)
print(f"Counter: {counter.counter_id} - {'Created' if created else 'Already exists'}")

# Create a queue if it doesn't exist
queue, created = Queue.objects.get_or_create(
    queue_id='Q001',
    counter=counter,
    defaults={
        'service_type': 'general',
        'is_active': True,
        'average_service_time': 5
    }
)
print(f"Queue: {queue.queue_id} - {'Created' if created else 'Already exists'}")

# Now add tokens to customer1
from queueapp.models import Token
from django.utils import timezone

customer = User.objects.get(username='customer1')
print(f"\nAdding 5 tokens to {customer.username}...")

created_tokens = []
for i in range(5):
    token_number = f"{customer.username}-{timezone.now().strftime('%Y%m%d%H%M%S')}-{i+1}"
    token = Token.objects.create(
        token_number=token_number,
        queue=queue,
        customer=customer,
        user=customer,
        status='generated',
        priority=1
    )
    created_tokens.append(token)
    print(f"Created token: {token.token_number}")

print(f"\nSuccessfully added {len(created_tokens)} tokens to {customer.username}")
