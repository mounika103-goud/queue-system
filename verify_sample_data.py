#!/usr/bin/env python
"""
Verify Sample Data Installation
Checks that all sample data is properly installed in the database
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from django.contrib.auth.models import User
from queueapp.models import Counter, Queue, Token, QueueAnalytics, Notification, UserRole

def verify_data():
    """Verify all sample data is installed"""
    
    print("\n" + "="*70)
    print("  ✅ SAMPLE DATA VERIFICATION REPORT")
    print("="*70)
    
    # Check counters
    print("\n📍 COUNTERS:")
    counter_count = Counter.objects.count()
    print(f"  Expected: 5 | Actual: {counter_count} | Status: {'✅ PASS' if counter_count == 5 else '❌ FAIL'}")
    for counter in Counter.objects.all():
        print(f"    • {counter.name} ({counter.counter_id}) - {counter.status}")
    
    # Check queues
    print("\n📋 QUEUES:")
    queue_count = Queue.objects.count()
    print(f"  Expected: 5 | Actual: {queue_count} | Status: {'✅ PASS' if queue_count == 5 else '❌ FAIL'}")
    for queue in Queue.objects.all():
        token_count = queue.tokens.count()
        print(f"    • {queue.service_type} Queue - {token_count} tokens")
    
    # Check tokens
    print("\n🎫 TOKENS:")
    token_count = Token.objects.count()
    print(f"  Expected: 28 | Actual: {token_count} | Status: {'✅ PASS' if token_count >= 20 else '❌ FAIL'}")
    
    print("\n  Token Status Distribution:")
    for status, label in Token.TOKEN_STATUS:
        count = Token.objects.filter(status=status).count()
        if count > 0:
            print(f"    • {label}: {count}")
    
    # Check notifications
    print("\n🔔 NOTIFICATIONS:")
    notif_count = Notification.objects.count()
    print(f"  Expected: 14+ | Actual: {notif_count} | Status: {'✅ PASS' if notif_count >= 10 else '❌ FAIL'}")
    print(f"  Types:")
    for ntype, label in Notification.NOTIFICATION_TYPES:
        count = Notification.objects.filter(notification_type=ntype).count()
        if count > 0:
            print(f"    • {label}: {count}")
    
    # Check analytics
    print("\n📊 ANALYTICS:")
    analytics_count = QueueAnalytics.objects.count()
    print(f"  Expected: 5+ | Actual: {analytics_count} | Status: {'✅ PASS' if analytics_count >= 5 else '❌ FAIL'}")
    
    # Check user assignments
    print("\n👥 USER ASSIGNMENTS:")
    customers = UserRole.objects.filter(role='customer')
    staff = UserRole.objects.filter(role='staff')
    print(f"  Customers: {customers.count()}")
    print(f"  Staff: {staff.count()}")
    
    # Check token assignments
    tokens_with_customers = Token.objects.filter(customer__isnull=False).count()
    print(f"  Tokens Assigned: {tokens_with_customers}/{token_count}")
    
    # Summary
    print("\n" + "="*70)
    print("  📊 SUMMARY")
    print("="*70)
    
    checks = [
        ("Counters (5)", counter_count == 5),
        ("Queues (5)", queue_count == 5),
        ("Tokens (28+)", token_count >= 20),
        ("Notifications (10+)", notif_count >= 10),
        ("Analytics (5+)", analytics_count >= 5),
        ("Customer Roles (7+)", customers.count() >= 7),
        ("Staff Roles (4+)", staff.count() >= 4),
    ]
    
    passed = 0
    for check_name, result in checks:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {check_name:.<40} {status}")
        if result:
            passed += 1
    
    print("\n" + "="*70)
    total = len(checks)
    print(f"  RESULT: {passed}/{total} checks passed")
    
    if passed == total:
        print("\n  🎉 ALL VERIFICATION CHECKS PASSED!")
        print("  ✅ Sample data is properly installed!")
        print("\n  Ready to use:")
        print("    • python manage.py runserver")
        print("    • Visit: http://localhost:8000/login/")
        print("    • Login with: customer1 / customer123 (or staff1 / admin)")
    else:
        print("\n  ⚠️  Some checks failed!")
        print("  Please run: python seed_dashboard_data.py")
    
    print("\n" + "="*70 + "\n")
    
    return passed == total

if __name__ == '__main__':
    success = verify_data()
    exit(0 if success else 1)
