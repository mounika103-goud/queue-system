#!/usr/bin/env python
"""
Reset all passwords to ensure login works
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from django.contrib.auth.models import User
from queueapp.models import UserRole

print("\n" + "="*70)
print("🔑 PASSWORD RESET UTILITY")
print("="*70 + "\n")

# Define credentials
credentials = {
    'admin': 'admin123',
    'staff1': 'staff123',
    'staff2': 'staff123',
    'staff3': 'staff123',
    'customer1': 'customer123',
    'customer2': 'customer123',
    'customer3': 'customer123',
    'customer4': 'customer123',
    'customer5': 'customer123',
}

print("Resetting passwords for all accounts...\n")

for username, password in credentials.items():
    try:
        user = User.objects.get(username=username)
        user.set_password(password)
        user.save()
        
        # Get role
        try:
            role = user.role.get_role_display()
        except Exception as e:
            role = "Unknown"
        
        print(f"✓ {username:15} → Password: {password:20} (Role: {role})")
    except User.DoesNotExist:
        print(f"✗ {username:15} → User not found")

print("\n" + "="*70)
print("✅ PASSWORD RESET COMPLETE!")
print("="*70 + "\n")

print("📋 LOGIN CREDENTIALS:\n")
print("ADMIN:")
print("   Username: admin")
print("   Password: admin123")
print("   URL:      http://localhost:8000/accounts/login/\n")

print("STAFF (Counter Manager):")
print("   Username: staff1, staff2, or staff3")
print("   Password: staff123")
print("   URL:      http://localhost:8000/accounts/login/\n")

print("CUSTOMER:")
print("   Username: customer1, customer2, customer3, customer4, or customer5")
print("   Password: customer123")
print("   URL:      http://localhost:8000/accounts/login/\n")

print("="*70)
print("🚀 Ready to login!")
print("="*70 + "\n")
