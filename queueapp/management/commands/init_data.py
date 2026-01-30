from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from queueapp.models import Counter, Queue, Token, UserRole
from datetime import datetime, timedelta
from django.utils import timezone
import random


class Command(BaseCommand):
    help = 'Initialize sample data for dashboard testing'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting data initialization...'))

        # Create admin user
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@bank.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            UserRole.objects.get_or_create(user=admin_user, defaults={'role': 'admin'})
            self.stdout.write(self.style.SUCCESS('✓ Created admin user'))

        # Create staff users
        staff_users = []
        for i in range(1, 4):
            staff_user, created = User.objects.get_or_create(
                username=f'staff{i}',
                defaults={
                    'email': f'staff{i}@bank.com',
                    'first_name': f'Staff',
                    'last_name': f'Member {i}'
                }
            )
            if created:
                staff_user.set_password('staff123')
                staff_user.save()
                UserRole.objects.get_or_create(user=staff_user, defaults={'role': 'staff'})
            staff_users.append(staff_user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(staff_users)} staff users'))

        # Create customers
        customer_users = []
        for i in range(1, 6):
            customer_user, created = User.objects.get_or_create(
                username=f'customer{i}',
                defaults={
                    'email': f'customer{i}@bank.com',
                    'first_name': f'Customer',
                    'last_name': f'{i}'
                }
            )
            if created:
                customer_user.set_password('customer123')
                customer_user.save()
                UserRole.objects.get_or_create(user=customer_user, defaults={'role': 'customer'})
            customer_users.append(customer_user)
        self.stdout.write(self.style.SUCCESS(f'✓ Created {len(customer_users)} customer users'))

        # Create counters
        counters = []
        for i in range(1, 4):
            counter, created = Counter.objects.get_or_create(
                counter_id=f'C{i}',
                defaults={
                    'name': f'Counter {i}',
                    'staff_member': staff_users[i-1] if i <= len(staff_users) else None,
                    'is_active': True,
                    'is_online': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created counter {counter.counter_id}'))
            counters.append(counter)

        # Create queues
        service_types = ['Deposits', 'Withdrawals', 'Account Opening', 'Loans', 'General Inquiry']
        queues = []
        for idx, service_type in enumerate(service_types):
            counter = counters[idx % len(counters)]
            queue, created = Queue.objects.get_or_create(
                queue_id=f'Q{idx+1}',
                defaults={
                    'service_type': service_type,
                    'counter': counter,
                    'is_active': True,
                    'average_service_time': random.randint(3, 10)
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created queue for {service_type}'))
            queues.append(queue)

        # Create tokens
        today = timezone.now()
        statuses = ['completed', 'cancelled', 'no_show', 'generated', 'waiting']
        token_count = 0

        for queue in queues:
            for i in range(1, 6):
                token_number = f"{queue.queue_id}-{today.strftime('%Y%m%d')}-{i:03d}"
                
                token, created = Token.objects.get_or_create(
                    token_number=token_number,
                    defaults={
                        'queue': queue,
                        'user': random.choice(customer_users),
                        'customer': random.choice(customer_users),
                        'counter': queue.counter if i <= 2 else None,
                        'status': random.choice(statuses),
                        'priority': random.randint(1, 3),
                        'generated_at': today - timedelta(hours=random.randint(0, 8)),
                    }
                )
                if created:
                    token_count += 1

        self.stdout.write(self.style.SUCCESS(f'✓ Created {token_count} tokens'))
        self.stdout.write(self.style.SUCCESS('✅ Data initialization complete!'))
        self.stdout.write(self.style.WARNING('\nTest Credentials:'))
        self.stdout.write(self.style.WARNING('Admin: admin / admin123'))
        self.stdout.write(self.style.WARNING('Staff: staff1, staff2, staff3 / staff123'))
        self.stdout.write(self.style.WARNING('Customer: customer1-5 / customer123'))
