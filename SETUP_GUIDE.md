# Smart Banking Queue Management System - Setup Guide

## Complete Setup Instructions

### 1. Environment Setup

#### Windows
```powershell
# Create virtual environment
python -m venv venv

# Activate virtual environment
venv\Scripts\activate

# Verify activation (should show (venv) in prompt)
```

#### macOS/Linux
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Verify activation (should show (venv) in prompt)
```

### 2. Install Dependencies

```bash
# Upgrade pip
pip install --upgrade pip

# Install from requirements.txt
pip install -r requirements.txt
```

### 3. Database Configuration

#### Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

#### Create Superuser (Admin Account)
```bash
python manage.py createsuperuser

# You'll be prompted to enter:
# Username: admin
# Email: admin@example.com
# Password: (enter secure password)
# Password (again): (confirm)
```

### 4. Create Initial Data (Optional)

#### Method 1: Django Shell
```bash
python manage.py shell
```

Then in the Python shell:
```python
from django.contrib.auth.models import User
from queueapp.models import UserRole, Counter, Queue

# Create a customer user
customer = User.objects.create_user(
    username='customer1',
    email='customer@example.com',
    password='password123',
    first_name='John',
    last_name='Doe'
)
UserRole.objects.create(user=customer, role='customer')

# Create a staff user
staff = User.objects.create_user(
    username='staff1',
    email='staff@example.com',
    password='password123',
    first_name='Jane',
    last_name='Smith'
)
UserRole.objects.create(user=staff, role='staff')

# Create a counter manager
manager = User.objects.create_user(
    username='manager1',
    email='manager@example.com',
    password='password123',
    first_name='Robert',
    last_name='Johnson'
)
UserRole.objects.create(user=manager, role='counter_manager')

# Create a counter
counter1 = Counter.objects.create(
    counter_id='C001',
    counter_name='Counter 1',
    description='Main banking counter',
    service_types='deposits, withdrawals, account_opening'
)

# Assign staff to counter
counter1.current_staff = staff
counter1.manager = manager
counter1.save()

# Create queues for different services
services = [
    ('deposits', 'Deposits', 5),
    ('withdrawals', 'Withdrawals', 5),
    ('account_opening', 'Account Opening', 10),
    ('general', 'General Inquiry', 3),
]

for service_type, service_name, avg_time in services:
    Queue.objects.create(
        queue_id=f'Q00{services.index((service_type, service_name, avg_time)) + 1}',
        service_type=service_type,
        counter=counter1,
        average_service_time=avg_time
    )

print("Initial data created successfully!")
exit()
```

### 5. Run Development Server

```bash
# Start the development server
python manage.py runserver

# Server will be available at http://localhost:8000/
# You can specify a different port if needed:
python manage.py runserver 8080
```

### 6. Access the Application

Open your browser and navigate to:

| URL | Purpose | Role |
|-----|---------|------|
| http://localhost:8000/ | Home page | Everyone |
| http://localhost:8000/admin/ | Django admin | Admin only |
| http://localhost:8000/dashboard/ | Main dashboard | Authenticated users |
| http://localhost:8000/customer/dashboard/ | Customer area | Customers |
| http://localhost:8000/staff/dashboard/ | Staff area | Staff |
| http://localhost:8000/admin/dashboard/ | Admin area | Admins |

### 7. Login Test Accounts

Use these credentials to test different roles:

```
Admin Account (created in step 3)
Username: admin
Password: (your chosen password)

Customer Account (if created in step 4)
Username: customer1
Password: password123

Staff Account (if created in step 4)
Username: staff1
Password: password123

Manager Account (if created in step 4)
Username: manager1
Password: password123
```

## Common Commands

### Start Server
```bash
python manage.py runserver
```

### Create New App
```bash
python manage.py startapp appname
```

### Make Migrations
```bash
python manage.py makemigrations
```

### Apply Migrations
```bash
python manage.py migrate
```

### Create Superuser
```bash
python manage.py createsuperuser
```

### Open Django Shell
```bash
python manage.py shell
```

### Collect Static Files (Production)
```bash
python manage.py collectstatic
```

### Run Tests
```bash
python manage.py test
```

### Check Deployment Readiness
```bash
python manage.py check --deploy
```

## Project Features to Explore

### Customer Features
1. **Get Token**: Navigate to `/customer/get-token/`
   - Select a service type
   - Choose priority level
   - Add optional notes
   - View token number

2. **Track Token**: View real-time status of your token
   - Current position in queue
   - Estimated wait time
   - Service timeline

3. **Token History**: View all your previous tokens
   - Service details
   - Wait times
   - Service durations

### Staff Features
1. **Staff Dashboard**: View current counter queue
   - Number of waiting customers
   - Service statistics
   - Quick actions

2. **Serve Queue**: Manage customer service
   - Call next customer
   - View customer details
   - Mark service complete

### Admin Features
1. **Admin Dashboard**: System overview
   - Key metrics
   - Counter status
   - Quick actions

2. **Analytics**: View detailed reports
   - Queue performance
   - Service metrics
   - Daily trends

3. **Manage Counters**: Configure counters
   - Add/edit counters
   - Assign staff
   - Set service types

4. **Manage Queues**: Configure queues
   - Create/edit queues
   - Set average service times
   - Manage queue status

## Troubleshooting

### Issue: Port 8000 Already in Use
```bash
# Kill the process on port 8000 (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use a different port
python manage.py runserver 8001
```

### Issue: Module Not Found
```bash
# Reinstall all requirements
pip install -r requirements.txt --force-reinstall
```

### Issue: Database Errors
```bash
# Reset database (WARNING: deletes all data)
python manage.py migrate zero queueapp
python manage.py migrate
python manage.py createsuperuser
```

### Issue: Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic

# Or in development, ensure staticfiles is in INSTALLED_APPS
# Check settings.py
```

### Issue: Templates Not Found
```bash
# Verify TEMPLATES configuration in settings.py
# Should include: 'DIRS': [BASE_DIR / 'templates']

# Verify templates folder exists and has content
python -c "import os; print(os.listdir('templates'))"
```

## File Checklist

Verify these files and folders exist:

```
✓ queueproject/
  ✓ __init__.py
  ✓ settings.py
  ✓ urls.py
  ✓ wsgi.py
  ✓ asgi.py

✓ queueapp/
  ✓ migrations/
  ✓ models.py
  ✓ views.py
  ✓ urls.py
  ✓ admin.py
  ✓ services.py
  ✓ permissions.py
  ✓ utils.py

✓ templates/
  ✓ base/
    ✓ base.html
    ✓ navbar.html
    ✓ sidebar.html
  ✓ customer/
    ✓ dashboard.html
    ✓ get_token.html
    ✓ token_status.html
    ✓ history.html
  ✓ staff/
    ✓ dashboard.html
    ✓ serve_queue.html
  ✓ admin/
    ✓ dashboard.html
    ✓ analytics.html
    ✓ manage_counters.html
    ✓ manage_queues.html
  ✓ home.html

✓ static/
  ✓ css/
    ✓ base.css
    ✓ dashboard.css
    ✓ animations.css
  ✓ js/
    ✓ realtime.js
    ✓ charts.js
    ✓ ui.js

✓ manage.py
✓ requirements.txt
✓ README.md
✓ PROJECT_SUMMARY.md
✓ SETUP_GUIDE.md
✓ .gitignore
```

## Next Steps

1. **Explore Admin Interface**
   - Navigate to `/admin/`
   - Login with superuser credentials
   - Browse data models
   - Add/edit data

2. **Test User Flows**
   - Create customer users
   - Generate tokens
   - Test queue operations
   - View analytics

3. **Customize Features**
   - Modify styles in `static/css/`
   - Add new views in `views.py`
   - Update models as needed
   - Create new templates

4. **Deploy to Production**
   - Follow Django deployment guide
   - Set up PostgreSQL database
   - Configure Gunicorn/nginx
   - Set up SSL/HTTPS
   - Configure static files

## Performance Tips

1. Use `python manage.py runserver --nothreading` for single-threaded testing
2. Install `django-debug-toolbar` for performance analysis
3. Use database indexes on frequently queried fields
4. Implement Redis caching for better performance
5. Use `select_related()` and `prefetch_related()` for query optimization

## Security Reminders

1. Never commit `.env` or `settings.py` with secrets to git
2. Always use HTTPS in production
3. Regularly update dependencies: `pip install --upgrade -r requirements.txt`
4. Use strong passwords for admin accounts
5. Enable HTTPS and HSTS headers in production
6. Set `DEBUG = False` in production
7. Use environment variables for sensitive configuration

## Getting Help

1. Check Django documentation: https://docs.djangoproject.com/
2. Review project comments and docstrings
3. Check console output for detailed error messages
4. Use Django debug toolbar for debugging
5. Check database logs for issues

---

**Happy Coding!** 🚀

For more information, refer to README.md and PROJECT_SUMMARY.md
