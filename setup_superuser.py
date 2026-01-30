import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from django.contrib.auth.models import User
from queueapp.models import UserRole

# Create superuser
username = 'superadmin'
email = 'superadmin@bank.com'
password = 'SuperAdmin123!'

if User.objects.filter(username=username).exists():
    print(f'✅ Superuser {username} already exists')
else:
    user = User.objects.create_superuser(username, email, password)
    UserRole.objects.create(user=user, role='admin', is_active=True)
    print(f'✅ Superuser Created!')
    print(f'Username: {username}')
    print(f'Password: {password}')
    print(f'Admin URL: http://localhost:8000/admin/')
