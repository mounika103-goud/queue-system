#!/usr/bin/env python
"""
Create Superuser
Creates an admin superuser account for Django admin panel access
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from django.contrib.auth.models import User
from queueapp.models import UserRole

def create_superuser():
    """Create a superuser account"""
    
    # Superuser details
    username = 'admin'
    email = 'admin@bank.com'
    password = 'admin123'
    
    print("\n" + "="*60)
    print("👤 Creating Superuser")
    print("="*60)
    
    # Check if superuser already exists
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f"\n⏭️  Superuser '{username}' already exists!")
        print(f"   Email: {user.email}")
        print(f"   Is Staff: {user.is_staff}")
        print(f"   Is Superuser: {user.is_superuser}")
        print(f"   Active: {user.is_active}")
        
        # Check if they have admin role
        try:
            role = user.role.role
            print(f"   Role: {role}")
        except:
            print("   Role: Not assigned")
        
        return
    
    try:
        # Create superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        # Assign admin role
        UserRole.objects.create(
            user=user,
            role='admin',
            is_active=True
        )
        
        print(f"\n✅ Superuser Created Successfully!")
        print(f"   Username: {username}")
        print(f"   Email: {email}")
        print(f"   Password: {password}")
        print(f"   Role: admin")
        print(f"\n📍 Access Admin Panel:")
        print(f"   URL: http://localhost:8000/admin/")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
        
    except Exception as e:
        print(f"\n❌ Error creating superuser: {str(e)}")

if __name__ == '__main__':
    create_superuser()
