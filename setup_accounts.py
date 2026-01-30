#!/usr/bin/env python
"""
Quick Setup Script - Ensure all accounts and data exist
Run this before accessing the dashboards
"""

import os
import django
import random
from django.contrib.auth.models import User
from queueapp.models import UserRole, Counter, Queue
from django.utils import timezone

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

def create_admin():
    """Create admin account"""
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
        UserRole.objects.get_or_create(
            user=admin_user,
            defaults={'role': 'admin'}
        )
        print("✓ Created admin user (admin/admin123)")
        return True
    else:
        print("✓ Admin user already exists")
        return False

def create_staff():
    """Create staff accounts"""
    created_count = 0
    for i in range(1, 4):
        staff_user, created = User.objects.get_or_create(
            username=f'staff{i}',
            defaults={
                'email': f'staff{i}@bank.com',
                'first_name': 'Staff',
                'last_name': f'Member {i}'
            }
        )
        if created:
            staff_user.set_password('staff123')
            staff_user.save()
            UserRole.objects.get_or_create(
                user=staff_user,
                defaults={'role': 'staff'}
            )
            created_count += 1
    
    if created_count > 0:
        print(f"✓ Created {created_count} staff users (staff1-3/staff123)")
    else:
        print("✓ Staff users already exist")
    return created_count > 0

def create_customers():
    """Create customer accounts"""
    created_count = 0
    for i in range(1, 6):
        customer_user, created = User.objects.get_or_create(
            username=f'customer{i}',
            defaults={
                'email': f'customer{i}@bank.com',
                'first_name': 'Customer',
                'last_name': f'{i}'
            }
        )
        if created:
            customer_user.set_password('customer123')
            customer_user.save()
            UserRole.objects.get_or_create(
                user=customer_user,
                defaults={'role': 'customer'}
            )
            created_count += 1
    
    if created_count > 0:
        print(f"✓ Created {created_count} customer users (customer1-5/customer123)")
    else:
        print("✓ Customer users already exist")
    return created_count > 0

def create_counters():
    """Create counter objects"""
    created_count = 0
    staff_users = User.objects.filter(username__startswith='staff')
    
    for i in range(1, 4):
        counter, created = Counter.objects.get_or_create(
            counter_id=f'C{i}',
            defaults={
                'name': f'Counter {i}',
                'staff_member': staff_users[i-1] if i <= staff_users.count() else None,
                'is_active': True,
                'is_online': True
            }
        )
        if created:
            created_count += 1
    
    if created_count > 0:
        print(f"✓ Created {created_count} counters (C1, C2, C3)")
    else:
        print("✓ Counters already exist")
    return created_count > 0

def create_queues():
    """Create queue objects"""
    created_count = 0
    service_types = ['deposits', 'withdrawals', 'loans', 'account_opening', 'general']
    counters = list(Counter.objects.all())
    
    for idx, service_type in enumerate(service_types):
        counter = counters[idx % len(counters)] if counters else None
        if counter:
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
                created_count += 1
    
    if created_count > 0:
        print(f"✓ Created {created_count} queues")
    else:
        print("✓ Queues already exist")
    return created_count > 0

def main():
    print("\n" + "="*60)
    print("🔐 Smart Banking Queue System - Setup Script")
    print("="*60 + "\n")
    
    print("Setting up test accounts and data...\n")
    
    create_admin()
    create_staff()
    create_customers()
    create_counters()
    create_queues()
    
    print("\n" + "="*60)
    print("✅ Setup Complete!")
    print("="*60)
    
    print("\n📋 TEST CREDENTIALS:\n")
    print("Admin:")
    print("  Username: admin")
    print("  Password: admin123\n")
    
    print("Staff (Counter Manager):")
    print("  Username: staff1, staff2, or staff3")
    print("  Password: staff123\n")
    
    print("Customer:")
    print("  Username: customer1, customer2, etc.")
    print("  Password: customer123\n")
    
    print("🚀 Ready to use! Start the server:\n")
    print("   python manage.py runserver\n")
    print("Then visit: http://localhost:8000/accounts/login/\n")

if __name__ == '__main__':
    main()
