"""
Quick setup script to seed realistic data into the dashboard
Run this from the project root: python seed_data.py
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.management import call_command
from datetime import timedelta
import random

from queueapp.models import Queue, Token, UserRole

User = get_user_model()


def seed_data():
    print("=" * 50)
    print("Dashboard Data Seeding Script")
    print("=" * 50)
    print()
    
    today = timezone.now().date()
    
    # Get or create sample queues
    queues = Queue.objects.filter(is_active=True)
    if not queues.exists():
        print("⚠ WARNING: No active queues found.")
        print("Please create queues first via admin panel.")
        return False
    
    # Get sample customers
    customers = list(UserRole.objects.filter(role='customer')[:10].values_list('user', flat=True))
    customers = User.objects.filter(id__in=customers)
    
    if not customers:
        print("⚠ WARNING: No customer users found.")
        print("Please create customer users first.")
        return False
    
    print(f"Found {len(queues)} active queues")
    print(f"Found {len(customers)} customer users")
    print()
    
    # Seed today's tokens
    print("Seeding today's tokens...")
    token_count = 0
    
    for queue in queues:
        num_tokens = random.randint(8, 15)
        
        for i in range(num_tokens):
            customer = random.choice(customers)
            status = random.choices(
                ['completed', 'waiting', 'called', 'being_served'],
                weights=[60, 20, 10, 10]
            )[0]
            
            token_number = random.randint(1000, 9999)
            
            token = Token(
                token_number=token_number,
                queue=queue,
                customer=customer,
                status=status,
                priority=random.choice([1, 1, 1, 2, 3]),
                generated_at=timezone.now() - timedelta(hours=random.randint(0, 8)),
            )
            
            # Set time fields based on status
            if status == 'completed':
                called_time = token.generated_at + timedelta(minutes=random.randint(3, 15))
                token.called_at = called_time
                token.service_started_at = called_time + timedelta(seconds=random.randint(10, 60))
                token.service_ended_at = token.service_started_at + timedelta(minutes=random.randint(2, 8))
            elif status == 'being_served':
                called_time = token.generated_at + timedelta(minutes=random.randint(2, 10))
                token.called_at = called_time
                token.service_started_at = called_time + timedelta(seconds=random.randint(10, 60))
            elif status == 'called':
                token.called_at = token.generated_at + timedelta(minutes=random.randint(2, 8))
            
            try:
                token.save()
                token_count += 1
            except Exception as e:
                print(f"  Error creating token: {e}")
    
    # Seed yesterday's tokens
    print(f"  ✓ Created {token_count} tokens for today")
    
    print("Seeding yesterday's tokens...")
    yesterday = today - timedelta(days=1)
    yesterday_tokens = 0
    
    for queue in queues:
        num_tokens = random.randint(6, 12)
        
        for i in range(num_tokens):
            customer = random.choice(customers)
            
            token_number = random.randint(1000, 9999)
            
            # Create a time yesterday
            yesterday_time = timezone.make_aware(
                timezone.datetime(
                    yesterday.year, yesterday.month, yesterday.day,
                    random.randint(8, 17), random.randint(0, 59)
                )
            )
            
            token = Token(
                token_number=token_number,
                queue=queue,
                customer=customer,
                status='completed',
                priority=random.choice([1, 1, 1, 2, 3]),
                generated_at=yesterday_time,
            )
            
            called_time = token.generated_at + timedelta(minutes=random.randint(3, 15))
            token.called_at = called_time
            token.service_started_at = called_time + timedelta(seconds=random.randint(10, 60))
            token.service_ended_at = token.service_started_at + timedelta(minutes=random.randint(2, 8))
            
            try:
                token.save()
                yesterday_tokens += 1
            except Exception as e:
                print(f"  Error creating token: {e}")
    
    print(f"  ✓ Created {yesterday_tokens} tokens for yesterday")
    print()
    
    print("=" * 50)
    print("✓ Dashboard data seeding complete!")
    print("=" * 50)
    print()
    print("You should now see realistic data in:")
    print("  • Admin Dashboard: /dashboard/admin/")
    print("  • Staff Dashboard: /dashboard/staff/")
    print("  • Customer Dashboard: /dashboard/")
    print()
    print("Metrics now include:")
    print("  ✓ Average wait times (3-15 minutes)")
    print("  ✓ Tokens served today")
    print("  ✓ Average service time (2-8 minutes)")
    print("  ✓ System efficiency (60%+)")
    print("  ✓ Queue status and load indicators")
    print()
    
    return True


if __name__ == '__main__':
    success = seed_data()
    sys.exit(0 if success else 1)
