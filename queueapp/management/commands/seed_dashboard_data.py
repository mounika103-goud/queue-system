"""
Management command to seed realistic queue data for demonstration
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
import random

from queueapp.models import Queue, Token, Counter, Notification

User = get_user_model()


class Command(BaseCommand):
    help = 'Seed realistic queue and token data for dashboard demonstration'

    def handle(self, *args, **options):
        today = timezone.now().date()
        
        # Get or create sample queues
        queues = Queue.objects.filter(is_active=True)
        if not queues.exists():
            self.stdout.write(self.style.WARNING('No active queues found. Please create queues first.'))
            return
        
        # Get sample customers
        customers = User.objects.filter(userrole__role='customer')[:5]
        
        if not customers.exists():
            self.stdout.write(self.style.WARNING('No customer users found. Please create customer users first.'))
            return
        
        # Create tokens for today
        token_number = 1000
        
        for queue in queues:
            # Create 8-15 tokens per queue for today
            num_tokens = random.randint(8, 15)
            
            for i in range(num_tokens):
                token_number += 1
                customer = random.choice(customers)
                status = random.choices(
                    ['completed', 'waiting', 'called', 'being_served'],
                    weights=[60, 20, 10, 10]
                )[0]
                
                # Create token
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
                
                token.save()
        
        # Create some tokens for yesterday
        yesterday = today - timedelta(days=1)
        yesterday_noon = timezone.make_aware(
            timezone.datetime.combine(yesterday, timezone.datetime.min.time())
        )
        
        for queue in queues:
            num_tokens = random.randint(6, 12)
            
            for i in range(num_tokens):
                token_number += 1
                customer = random.choice(customers)
                
                token = Token(
                    token_number=token_number,
                    queue=queue,
                    customer=customer,
                    status='completed',
                    priority=random.choice([1, 1, 1, 2, 3]),
                    generated_at=yesterday_noon + timedelta(hours=random.randint(0, 8), minutes=random.randint(0, 59)),
                )
                
                called_time = token.generated_at + timedelta(minutes=random.randint(3, 15))
                token.called_at = called_time
                token.service_started_at = called_time + timedelta(seconds=random.randint(10, 60))
                token.service_ended_at = token.service_started_at + timedelta(minutes=random.randint(2, 8))
                
                token.save()
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ Successfully seeded {num_tokens * len(queues) * 2} tokens across {len(queues)} queues')
        )
        self.stdout.write(
            self.style.SUCCESS('Dashboard should now display realistic data!')
        )
