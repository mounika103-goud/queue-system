#!/usr/bin/env python
"""
Test Authentication Flow
This script tests the complete registration and login workflow
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from django.contrib.auth.models import User
from queueapp.models import UserRole

def test_registration():
    """Test user registration flow"""
    print("\n" + "="*60)
    print("🧪 Testing Registration & Login Flow")
    print("="*60)
    
    # Test data
    test_users = [
        {
            'username': 'testcustomer1',
            'email': 'customer1@bank.com',
            'password': 'TestPass123!',
            'first_name': 'John',
            'last_name': 'Doe',
            'role': 'customer'
        },
        {
            'username': 'teststaff1',
            'email': 'staff1@bank.com',
            'password': 'TestPass123!',
            'first_name': 'Jane',
            'last_name': 'Smith',
            'role': 'staff'
        },
        {
            'username': 'testadmin1',
            'email': 'admin1@bank.com',
            'password': 'AdminPass123!',
            'first_name': 'Admin',
            'last_name': 'User',
            'role': 'admin'
        },
    ]
    
    created_count = 0
    
    for user_data in test_users:
        username = user_data['username']
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"\n⏭️  User '{username}' already exists, skipping...")
            continue
        
        try:
            # Create user
            user = User.objects.create_user(
                username=username,
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name']
            )
            
            # Assign role
            UserRole.objects.create(
                user=user,
                role=user_data['role'],
                is_active=True
            )
            
            created_count += 1
            
            print(f"\n✅ User Created Successfully!")
            print(f"   Username: {username}")
            print(f"   Email: {user_data['email']}")
            print(f"   Password: {user_data['password']}")
            print(f"   Role: {user_data['role'].upper()}")
            print(f"   Name: {user_data['first_name']} {user_data['last_name']}")
            
        except Exception as e:
            print(f"\n❌ Error creating user '{username}': {str(e)}")
    
    # Display summary
    print("\n" + "="*60)
    print(f"📊 Summary: {created_count} users created successfully")
    print("="*60)
    
    # Display all users
    print("\n📋 All Users in Database:")
    print("-" * 60)
    all_users = User.objects.all()
    
    for user in all_users:
        try:
            role = user.role.role
        except:
            role = "Not assigned"
        
        print(f"\n👤 {user.username}")
        print(f"   Name: {user.get_full_name()}")
        print(f"   Email: {user.email}")
        print(f"   Role: {role}")
        print(f"   Active: {user.is_active}")
        print(f"   Created: {user.date_joined}")
    
    print("\n" + "="*60)
    print("✨ Test Complete!")
    print("="*60)

def test_login_credentials():
    """Verify login credentials work"""
    print("\n" + "="*60)
    print("🔐 Testing Login Credentials")
    print("="*60)
    
    from django.contrib.auth import authenticate
    
    credentials = [
        ('testcustomer1', 'TestPass123!'),
        ('teststaff1', 'TestPass123!'),
        ('testadmin1', 'AdminPass123!'),
    ]
    
    for username, password in credentials:
        user = authenticate(username=username, password=password)
        
        if user is not None:
            try:
                role = user.role.role
            except:
                role = "Not assigned"
            
            print(f"\n✅ Login Success: {username}")
            print(f"   Role: {role}")
            print(f"   Email: {user.email}")
        else:
            print(f"\n❌ Login Failed: {username}")

if __name__ == '__main__':
    test_registration()
    test_login_credentials()
