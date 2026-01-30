#!/usr/bin/env python
"""
Create demo accounts for testing
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from django.contrib.auth.models import User
from queueapp.models import UserRole

# Create admin
admin_user, created = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@bank.com',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    admin_user.set_password('admin123')
    admin_user.save()
    print("✓ Created admin user")
else:
    print("✓ Admin user already exists")

UserRole.objects.get_or_create(user=admin_user, defaults={'role': 'admin'})

# Create customers
print("\nCreating customers...")
for i in range(1, 6):
    customer_user, created = User.objects.get_or_create(
        username=f'customer{i}',
        defaults={
            'email': f'customer{i}@bank.com',
        }
    )
    if created:
        customer_user.set_password('customer123')
        customer_user.save()
    UserRole.objects.get_or_create(user=customer_user, defaults={'role': 'customer'})

print("✓ Created 5 customer users")

# Create staff
print("\nCreating staff...")
for i in range(1, 4):
    staff_user, created = User.objects.get_or_create(
        username=f'staff{i}',
        defaults={
            'email': f'staff{i}@bank.com',
        }
    )
    if created:
        staff_user.set_password('staff123')
        staff_user.save()
    UserRole.objects.get_or_create(user=staff_user, defaults={'role': 'staff'})

print("✓ Created 3 staff users")

print("\n" + "="*70)
print("✅ ALL DEMO ACCOUNTS CREATED!")
print("="*70)
print("\n📋 LOGIN CREDENTIALS:\n")
print("ADMIN:")
print("   Username: admin")
print("   Password: admin123")
print("\nCUSTOMER:")
print("   Username: customer1-5")
print("   Password: customer123")
print("\nSTAFF:")
print("   Username: staff1-3")
print("   Password: staff123")
print("\n🚀 Visit: http://127.0.0.1:8000/accounts/login/")
print("="*70)
