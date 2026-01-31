#!/usr/bin/env python
"""
Realistic Demo Data for Dashboard
Creates a realistic small dataset for demo purposes:
- 2-3 active queues
- 20-30 total tokens
- Mix of statuses (completed, waiting, called, serving)
- Realistic wait and service times
"""

import os
import django
from datetime import datetime, timedelta
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from django.contrib.auth.models import User
from queueapp.models import Counter, Queue, Token, UserRole
from django.utils import timezone

def clear_data():
    """Clear demo data"""
    print("\n🗑️  Clearing demo data...")
    Token.objects.all().delete()
    Queue.objects.all().delete()
    Counter.objects.all().delete()
    print("✅ Data cleared!")

def create_demo_counters():
    """Create 3 demo counters"""
    print("\n📍 Creating demo counters...")
    
    counters_data = [
        {'counter_id': 'CTR-01', 'name': 'Counter 1', 'status': 'active'},
        {'counter_id': 'CTR-02', 'name': 'Counter 2', 'status': 'active'},
        {'counter_id': 'CTR-03', 'name': 'Counter 3', 'status': 'active'},
    ]
    
    counters = {}
    for counter_data in counters_data:
        counter = Counter.objects.create(
            counter_id=counter_data['counter_id'],
            name=counter_data['name'],
        )
        counters[counter_data['counter_id']] = counter
        print(f"  ✅ Created: {counter_data['name']}")
    
    return counters

def create_demo_queues(counters):
    """Create 3 demo queues"""
    print("\n🏦 Creating demo queues...")
    
    queues_data = [
        {
            'service_type': 'deposits',
            'counter': list(counters.values())[0],
            'avg_service': 5,
        },
        {
            'service_type': 'withdrawals',
            'counter': list(counters.values())[1],
            'avg_service': 6,
        },
        {
            'service_type': 'general',
            'counter': list(counters.values())[2],
            'avg_service': 7,
        },
    ]
    
    queues = {}
    for queue_data in queues_data:
        queue = Queue.objects.create(
            queue_id=f"Q-{queue_data['service_type'].upper()}-001",
            service_type=queue_data['service_type'],
            is_active=True,
            average_service_time=queue_data['avg_service'],
            counter=queue_data['counter'],
        )
        queues[queue_data['service_type']] = queue
        print(f"  ✅ Created: {queue_data['service_type'].title()} Queue (Avg service: {queue_data['avg_service']} min)")
    
    return queues

def create_demo_tokens(queues):
    """Create realistic demo tokens with better variation (100+ tokens)"""
    print("\n🎫 Creating demo tokens with realistic distribution...")
    
    customer_users = list(User.objects.filter(role__role='customer')[:5])
    staff_users = list(User.objects.filter(role__role='staff'))
    
    if not customer_users:
        print("  ⚠️  No customer users found!")
        return
    
    token_count = 0
    now = timezone.now()
    global_token_id = 5000
    
    # Create tokens across each queue
    for queue in queues.values():
        queue_avg_service = queue.average_service_time
        
        # Completed tokens (60% of traffic)
        for i in range(35):
            global_token_id += 1
            token_number = f"{queue.service_type.upper()[:3]}-{global_token_id}"
            
            minutes_ago = random.randint(5, 300)
            service_duration = random.randint(queue_avg_service - 2, queue_avg_service + 4)
            
            generated_at = now - timedelta(minutes=minutes_ago + service_duration + random.randint(1, 3))
            called_at = now - timedelta(minutes=minutes_ago + service_duration)
            service_started_at = called_at
            service_ended_at = now - timedelta(minutes=minutes_ago)
            
            Token.objects.create(
                token_number=token_number,
                queue=queue,
                customer=random.choice(customer_users),
                user=random.choice(customer_users),
                counter=queue.counter,
                served_by=random.choice(staff_users),
                status='completed',
                priority=random.choice([1, 1, 1, 2, 2, 3]),
                generated_at=generated_at,
                called_at=called_at,
                service_started_at=service_started_at,
                service_ended_at=service_ended_at,
                estimated_wait_time=random.randint(queue_avg_service * 2, queue_avg_service * 5),
            )
            token_count += 1
        
        # Waiting tokens (25% of traffic)
        for i in range(15):
            global_token_id += 1
            token_number = f"{queue.service_type.upper()[:3]}-{global_token_id}"
            generated_at = now - timedelta(minutes=random.randint(2, 45))
            
            Token.objects.create(
                token_number=token_number,
                queue=queue,
                customer=random.choice(customer_users),
                user=random.choice(customer_users),
                counter=None,
                status='waiting',
                priority=random.choice([1, 1, 1, 2, 2, 3]),
                generated_at=generated_at,
                called_at=None,
                service_started_at=None,
                service_ended_at=None,
                estimated_wait_time=random.randint(queue_avg_service * 3, queue_avg_service * 6),
            )
            token_count += 1
        
        # Called tokens (8%)
        for i in range(5):
            global_token_id += 1
            token_number = f"{queue.service_type.upper()[:3]}-{global_token_id}"
            generated_at = now - timedelta(minutes=random.randint(10, 40))
            called_at = now - timedelta(minutes=random.randint(2, 15))
            
            Token.objects.create(
                token_number=token_number,
                queue=queue,
                customer=random.choice(customer_users),
                user=random.choice(customer_users),
                counter=queue.counter,
                served_by=random.choice(staff_users),
                status='called',
                priority=random.choice([1, 1, 1, 2, 2, 3]),
                generated_at=generated_at,
                called_at=called_at,
                service_started_at=None,
                service_ended_at=None,
                estimated_wait_time=random.randint(queue_avg_service, queue_avg_service * 3),
            )
            token_count += 1
        
        # Serving tokens (3%)
        for i in range(2):
            global_token_id += 1
            token_number = f"{queue.service_type.upper()[:3]}-{global_token_id}"
            generated_at = now - timedelta(minutes=random.randint(15, 35))
            called_at = now - timedelta(minutes=random.randint(3, 12))
            service_started_at = called_at
            
            Token.objects.create(
                token_number=token_number,
                queue=queue,
                customer=random.choice(customer_users),
                user=random.choice(customer_users),
                counter=queue.counter,
                served_by=random.choice(staff_users),
                status='serving',
                priority=random.choice([1, 1, 1, 2, 2, 3]),
                generated_at=generated_at,
                called_at=called_at,
                service_started_at=service_started_at,
                service_ended_at=None,
                estimated_wait_time=random.randint(queue_avg_service * 2, queue_avg_service * 4),
            )
            token_count += 1
        
        # Generated tokens (4%)
        for i in range(3):
            global_token_id += 1
            token_number = f"{queue.service_type.upper()[:3]}-{global_token_id}"
            generated_at = now - timedelta(minutes=random.randint(0, 5))
            
            Token.objects.create(
                token_number=token_number,
                queue=queue,
                customer=random.choice(customer_users),
                user=random.choice(customer_users),
                counter=None,
                status='generated',
                priority=random.choice([1, 1, 1, 2, 2, 3]),
                generated_at=generated_at,
                called_at=None,
                service_started_at=None,
                service_ended_at=None,
                estimated_wait_time=random.randint(queue_avg_service * 3, queue_avg_service * 7),
            )
            token_count += 1
    
    print(f"  ✅ Created {token_count} realistic demo tokens")

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 QUEUE MANAGEMENT SYSTEM - DEMO DATA SEEDER")
    print("=" * 60)
    
    try:
        clear_data()
        counters = create_demo_counters()
        queues = create_demo_queues(counters)
        create_demo_tokens(queues)
        
        # Print summary
        print("\n" + "=" * 60)
        print("✨ DEMO DATA SEEDING COMPLETED!")
        print("=" * 60)
        print(f"📊 Summary:")
        print(f"   ✓ Counters: {Counter.objects.count()}")
        print(f"   ✓ Queues: {Queue.objects.count()}")
        print(f"   ✓ Tokens: {Token.objects.count()}")
        print(f"   ✓ Users: {User.objects.count()}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
