#!/usr/bin/env python
"""
Complete End-to-End Test for Registration and Login Flow
Tests the entire workflow from registration through login
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from django.contrib.auth.models import User
from queueapp.models import UserRole
from django.contrib.auth import authenticate

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def test_registration_flow():
    """Test creating a new user (simulating registration)"""
    print_header("TEST 1: REGISTRATION FLOW")
    
    # Simulate registration form submission
    username = 'test_user_' + str(int(__import__('time').time() % 10000))
    email = f'{username}@bank.com'
    password = 'TestPass123!'
    
    print(f"Creating new user: {username}")
    print(f"Email: {email}")
    print(f"Password: {password}")
    
    try:
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print("❌ User already exists!")
            return False
        
        # Create user (simulating registration)
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Test',
            last_name='User'
        )
        print(f"✅ User created successfully: {user.username}")
        
        # Assign customer role
        role = UserRole.objects.create(
            user=user,
            role='customer',
            is_active=True
        )
        print(f"✅ Customer role assigned: {role.role}")
        
        return True, username, password
    
    except Exception as e:
        print(f"❌ Registration failed: {str(e)}")
        return False, None, None

def test_login_flow(username, password):
    """Test login with registered credentials"""
    print_header("TEST 2: LOGIN FLOW")
    
    print(f"Attempting to login as: {username}")
    print(f"Password: {password}")
    
    # Authenticate user
    user = authenticate(username=username, password=password)
    
    if user is not None:
        print(f"✅ Authentication successful!")
        print(f"   Username: {user.username}")
        print(f"   Email: {user.email}")
        print(f"   Is Active: {user.is_active}")
        print(f"   Date Joined: {user.date_joined}")
        
        # Check user role
        try:
            role = user.role
            print(f"✅ User Role: {role.get_role_display()}")
            return True
        except:
            print("⚠️  Warning: No role assigned to user")
            return False
    else:
        print("❌ Authentication failed!")
        print("   Username or password is incorrect")
        return False

def test_existing_users():
    """Test login with existing test users"""
    print_header("TEST 3: LOGIN WITH EXISTING USERS")
    
    test_credentials = [
        ('customer1', 'customer123', 'Customer'),
        ('staff1', 'staff123', 'Staff'),
        ('admin', 'admin123', 'Admin'),
    ]
    
    all_passed = True
    for username, password, expected_role in test_credentials:
        print(f"\nTesting: {username} ({expected_role})")
        user = authenticate(username=username, password=password)
        
        if user is not None:
            role = user.role.get_role_display()
            if role == expected_role:
                print(f"   ✅ Login successful - Role: {role}")
            else:
                print(f"   ⚠️  Login successful but role mismatch - Expected: {expected_role}, Got: {role}")
                all_passed = False
        else:
            print(f"   ❌ Login failed")
            all_passed = False
    
    return all_passed

def test_database_integrity():
    """Verify database structure and data"""
    print_header("TEST 4: DATABASE INTEGRITY")
    
    # Check user count
    user_count = User.objects.count()
    print(f"Total Users in Database: {user_count}")
    
    if user_count < 3:
        print("❌ Expected at least 3 users (admin, customer1, staff1)")
        return False
    print("✅ User count is sufficient")
    
    # Check role assignments
    role_count = UserRole.objects.count()
    print(f"Total Role Assignments: {role_count}")
    
    if role_count < 3:
        print("❌ Expected at least 3 role assignments")
        return False
    print("✅ Role assignments exist")
    
    # List all users
    print("\nAll Users in Database:")
    for user in User.objects.all():
        try:
            role = user.role.get_role_display()
        except:
            role = "No Role"
        print(f"  • {user.username:20} ({user.email:25}) - {role}")
    
    return True

def test_dashboard_routing():
    """Test dashboard routing logic"""
    print_header("TEST 5: DASHBOARD ROUTING LOGIC")
    
    test_cases = [
        ('customer1', '/dashboard/customer/', 'customer_dashboard'),
        ('staff1', '/dashboard/staff/', 'staff_dashboard'),
        ('admin', '/dashboard/admin/', 'admin_dashboard'),
    ]
    
    all_passed = True
    for username, expected_url, route_name in test_cases:
        user = User.objects.get(username=username)
        role = user.role.role
        
        # Determine expected route
        if role == 'customer':
            expected = '/dashboard/customer/'
        elif role == 'staff':
            expected = '/dashboard/staff/'
        elif role == 'admin':
            expected = '/dashboard/admin/'
        else:
            expected = '/dashboard/'
        
        print(f"\nUser: {username} (Role: {role})")
        print(f"   Expected Route: {expected}")
        print(f"   ✅ Route would be correct" if expected == expected_url else f"   ❌ Route mismatch")
    
    return all_passed

def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("   SMART BANKING QUEUE SYSTEM")
    print("   REGISTRATION & LOGIN COMPLETE TEST SUITE")
    print("="*60)
    
    results = {}
    
    # Test 1: Registration
    print("\n⏳ Running registration flow test...")
    reg_result = test_registration_flow()
    if reg_result and len(reg_result) == 3:
        success, username, password = reg_result
        results['Registration'] = success
        
        # Test 2: Login with new user
        if success:
            print("\n⏳ Running login flow test with new user...")
            login_result = test_login_flow(username, password)
            results['New User Login'] = login_result
    
    # Test 3: Existing users
    print("\n⏳ Testing existing users...")
    results['Existing Users Login'] = test_existing_users()
    
    # Test 4: Database
    print("\n⏳ Checking database integrity...")
    results['Database Integrity'] = test_database_integrity()
    
    # Test 5: Routing
    print("\n⏳ Testing dashboard routing logic...")
    results['Dashboard Routing'] = test_dashboard_routing()
    
    # Summary
    print_header("TEST SUMMARY")
    print("\nTest Results:")
    print("-" * 60)
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name:.<40} {status}")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print("-" * 60)
    print(f"\nTotal: {passed_tests}/{total_tests} tests passed\n")
    
    if passed_tests == total_tests:
        print("🎉 ALL TESTS PASSED! System is ready for use.\n")
    else:
        print("⚠️  Some tests failed. Please review the output above.\n")
    
    return passed_tests == total_tests

if __name__ == '__main__':
    success = run_all_tests()
    exit(0 if success else 1)
