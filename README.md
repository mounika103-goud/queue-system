# Smart Banking Queue Management System

A Django-based web application for managing customer queues in banking systems with real-time updates, priority handling, and comprehensive analytics.

## Features

- **Digital Token System**: Generate and manage digital tokens instead of traditional waiting lines
- **Real-time Queue Updates**: Live updates on queue status and token position
- **Priority Service**: Special queues for senior citizens, PWD, VIPs, and emergencies
- **Role-based Access Control**: Different dashboards for customers, staff, and administrators
- **Analytics & Reports**: Comprehensive metrics on queue performance and customer satisfaction
- **Responsive Design**: Works seamlessly on desktop, tablet, and mobile devices
- **Notification System**: Real-time notifications when tokens are called

## Project Structure

```
queueproject/
├── queueproject/              # Project configuration
│   ├── settings.py           # Django settings
│   ├── urls.py               # Project-level URL routing
│   ├── wsgi.py               # WSGI configuration
│   └── asgi.py               # ASGI configuration (for WebSockets)
│
├── queueapp/                 # Main application
│   ├── models.py             # Database models
│   ├── views.py              # View functions
│   ├── urls.py               # App-level URL routing
│   ├── services.py           # Business logic
│   ├── permissions.py        # Role-based access control
│   ├── utils.py              # Helper functions
│   └── admin.py              # Django admin configuration
│
├── templates/                # HTML templates
│   ├── base/                 # Base templates
│   │   ├── base.html        # Main layout
│   │   ├── navbar.html      # Navigation bar
│   │   └── sidebar.html     # Sidebar navigation
│   ├── customer/             # Customer pages
│   ├── staff/                # Staff pages
│   └── admin/                # Admin pages
│
├── static/                   # Static files
│   ├── css/                  # Stylesheets
│   ├── js/                   # JavaScript files
│   └── images/               # Images
│
└── manage.py                 # Django management script
```

## Installation & Setup

### Prerequisites
- Python 3.9+
- pip (Python package manager)
- Virtual environment (recommended)

### Step 1: Create Virtual Environment
```bash
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install django==4.2.27
pip install djangorestframework
pip install django-cors-headers
```

### Step 3: Database Setup
```bash
# Run migrations
python manage.py migrate

# Create superuser for admin panel
python manage.py createsuperuser
```

### Step 4: Create Initial Data
```bash
python manage.py shell

# In the Django shell:
from django.contrib.auth.models import User
from queueapp.models import UserRole, Counter, Queue

# Create a test user
user = User.objects.create_user('testuser', 'test@example.com', 'password123')
UserRole.objects.create(user=user, role='customer')

# Create a counter
counter = Counter.objects.create(
    counter_id='C001',
    counter_name='Counter 1',
    service_types='deposits, withdrawals'
)

# Create a queue
queue = Queue.objects.create(
    queue_id='Q001',
    service_type='deposits',
    counter=counter
)
```

### Step 5: Run Development Server
```bash
python manage.py runserver

# Visit http://localhost:8000/
```

## User Roles

### Customer
- Generate tokens for services
- Track token status in real-time
- View service history
- Receive notifications

### Staff
- View assigned counter's queue
- Call next customer
- Manage active tokens
- Update service status

### Counter Manager
- Manage staff assignments
- Monitor counter performance
- Generate counter reports

### Administrator
- Full system access
- Manage counters and queues
- View analytics and reports
- User management
- System configuration

## API Endpoints

### Queue Management
- `GET /api/queue-status/<queue_id>/` - Get queue status
- `POST /api/queue/generate-token/` - Generate new token
- `POST /api/queue/call-next/` - Call next token

### Token Management
- `GET /api/token-status/<token_id>/` - Get token status
- `POST /api/token/<token_id>/complete/` - Complete service

### Notifications
- `GET /api/notifications/` - Get user notifications

## Models

### UserRole
- Defines user roles (customer, staff, counter_manager, admin)
- One-to-one relationship with User model

### Counter
- Represents physical or virtual banking counters
- Manages service types and staff assignments

### Queue
- Service-specific queues at each counter
- Tracks waiting time and service statistics

### Token
- Issued to customers for queue management
- Tracks token status, priority, and service times

### QueueAnalytics
- Stores daily analytics and performance metrics
- Used for reporting and optimization

### Notification
- Real-time notifications for customers and staff

## Customization

### Adding New Service Types
Edit `Queue.SERVICE_TYPES` in `models.py`:
```python
SERVICE_TYPES = [
    ('your_service', 'Your Service'),
    # ... other services
]
```

### Modifying Styling
- Update CSS files in `static/css/`
- Main styles: `base.css`, `dashboard.css`, `animations.css`

### Adding New Features
1. Create models in `models.py`
2. Add views in `views.py`
3. Create templates in `templates/`
4. Register URLs in `urls.py`

## Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn queueproject.wsgi:application --bind 0.0.0.0:8000
```

### Production Settings
1. Set `DEBUG = False` in settings.py
2. Update `ALLOWED_HOSTS`
3. Set `SECRET_KEY` to a strong random value
4. Use PostgreSQL or MySQL instead of SQLite
5. Configure CSRF settings
6. Set up HTTPS/SSL

## Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Database Errors
```bash
python manage.py migrate --fake-initial
python manage.py migrate
```

### Missing Templates
Ensure `TEMPLATES[0]['DIRS']` includes the templates folder in settings.py

## Performance Tips

1. Use database indexing on frequently queried fields
2. Implement caching for queue status
3. Use WebSockets for real-time updates (via Django Channels)
4. Optimize database queries with `select_related()` and `prefetch_related()`
5. Use pagination for large datasets

## Security Considerations

1. Always use HTTPS in production
2. Implement rate limiting for API endpoints
3. Validate and sanitize all user inputs
4. Use CSRF protection (enabled by default)
5. Implement proper authentication and authorization
6. Regularly update dependencies
7. Use environment variables for sensitive data

## Future Enhancements

- WebSocket integration for real-time updates (Django Channels)
- Mobile app (React Native/Flutter)
- SMS/Email notifications
- Advanced analytics with machine learning
- Multi-language support
- Biometric customer identification
- Integration with banking systems APIs

## License

This project is licensed under the MIT License.

## Support

For issues, questions, or suggestions, please contact the development team.

## Contributors

- Project Team (EY)

---

**Last Updated**: January 2026
