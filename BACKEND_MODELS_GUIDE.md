# Backend Implementation Guide - Smart Banking Queue Management System

## 📋 Overview

This document provides comprehensive guidance for the Django backend implementation of the Smart Banking Queue Management System with multi-bank, multi-branch, and slot booking support.

## 🗂️ Project Structure

```
queueapp/
├── models.py           # Data models (13 models)
├── services.py         # Business logic layer
├── admin.py            # Django admin configuration
├── views.py            # Views (thin, use services)
├── urls.py             # URL routing
├── api.py              # REST API endpoints
├── tests.py            # Test suite
├── permissions.py      # Permission classes
├── utils.py            # Helper functions
└── migrations/         # Database migrations
```

## 🗄️ Database Models

### 1. UserRole
Defines user roles in the system
- **Role Choices:** customer, staff, counter_manager, branch_manager, admin
- **Fields:** user, role, is_active, created_at, updated_at
- **Methods:** get_user_role(user)

### 2. Bank
Top-level banking entity
- **Fields:** bank_code (unique), name, description, status, phone_number, email, admin
- **Status:** active, inactive, under_maintenance
- **Relationships:** branches (reverse), managed_banks (admin)

### 3. Branch
Bank branch location
- **Fields:** bank, branch_code, name, description, status, address, city, state, postal_code, opening_time, closing_time, manager
- **Unique Constraint:** (bank, branch_code)
- **Methods:** is_open(), get_active_counters()

### 4. Service
Banking services offered
- **Service Types:** deposits, withdrawals, loans, account_opening, account_maintenance, cash_counter, general_inquiry, foreign_exchange
- **Fields:** service_code (unique), service_type, name, description, average_service_time, is_active, requires_appointment, max_queue_size

### 5. Counter
Physical or virtual counter at a branch
- **Fields:** branch, counter_id, name, description, status, service, manager, staff_member, is_active, is_online, is_busy
- **Unique Constraint:** (branch, counter_id)
- **Methods:** get_current_token(), get_waiting_tokens()

### 6. Slot
Time slot for appointments
- **Slot Status:** available, partially_booked, fully_booked, closed
- **Fields:** counter, service, slot_date, slot_start_time, slot_end_time, max_capacity, current_bookings, status, is_active
- **Unique Constraint:** (counter, slot_date, slot_start_time)
- **Indexes:** (slot_date, status), (counter, slot_date)
- **Methods:** clean(), save(), available_slots (property), is_fully_booked (property)

### 7. SlotBooking
Customer slot booking records
- **Booking Status:** confirmed, cancelled, completed, no_show
- **Fields:** booking_id (unique), user, slot, service, booking_date, status, customer_notes, cancellation_reason, cancelled_at, is_reminder_sent, reminder_sent_at
- **Unique Constraint:** (user, slot)
- **Methods:** clean(), cancel(reason)

### 8. Queue
Queue for specific service at a counter
- **Fields:** queue_id (unique), counter, service, is_active, average_service_time, current_wait_time
- **Unique Constraint:** (counter, service)
- **Methods:** get_waiting_count(), get_active_tokens()

### 9. Token
Token issued to customers
- **Token Status:** generated, waiting, called, serving, completed, cancelled, no_show
- **Priority Levels:** 1=Normal, 2=Senior/PWD, 3=VIP, 4=Emergency
- **Fields:** token_number (unique), queue, customer, counter, status, priority, generated_at, called_at, completed_at, cancelled_at, served_by, service_started_at, service_ended_at, timing metrics, cancellation_reason, skip_count, customer_notes, slot_booking
- **Indexes:** (status, queue), (customer, status), (generated_at)
- **Properties:** wait_duration, service_duration, get_priority_display_full()

### 10. QueueAnalytics
Daily analytics for queues
- **Fields:** date, queue, total_tokens, served_tokens, cancelled_tokens, no_show_tokens, avg_wait_time, avg_service_time, peak_hour, max_queue_length
- **Unique Constraint:** (date, queue)
- **Indexes:** (date), (queue, date)
- **Property:** served_percentage

### 11. Notification
User notifications
- **Notification Types:** token_called, token_confirmed, slot_reminder, queue_update, system_alert, service_alert, booking_confirmation
- **Fields:** user, notification_type, title, message, token, slot_booking, is_read, read_at, created_at
- **Indexes:** (user, is_read), (created_at)
- **Methods:** mark_as_read()

### 12. AuditLog
Audit trail for compliance
- **Action Types:** token_generated, token_called, token_served, booking_created, booking_cancelled, counter_activated, counter_deactivated, staff_assigned, other
- **Fields:** action_type, description, user, token, slot_booking, ip_address, user_agent, created_at
- **Indexes:** (action_type, created_at), (user, created_at)

## 🔧 Business Logic Services (services.py)

### TokenService
Handles token generation and lifecycle management

**Methods:**
- `generate_token_number(counter)` - Generate unique token number
- `create_token(queue, customer, priority=1, from_booking=None)` - Create new token
- `call_token(token)` - Call token to counter
- `start_service(token, staff_member)` - Start serving token
- `complete_service(token)` - Complete service
- `cancel_token(token, reason="")` - Cancel token
- `mark_no_show(token)` - Mark as no-show

### SlotBookingService
Manages slot bookings and availability

**Methods:**
- `create_booking(user, slot, service, notes="")` - Create booking with overbooking prevention
- `cancel_booking(booking, reason="")` - Cancel booking
- `get_available_slots(service, branch, days_ahead=7)` - Query available slots
- `send_reminders()` - Send 24-hour reminders (scheduled task)

### QueueService
Manages queues and queue operations

**Methods:**
- `get_next_token(counter)` - Get next token respecting priority
- `get_queue_statistics(queue)` - Get queue stats for the day
- `get_branch_queue_status(branch)` - Get status for all branch counters

### NotificationService
Sends notifications to users

**Methods:**
- `send_token_called_notification(token)` - When token is called
- `send_token_confirmed_notification(token)` - When token confirmed
- `send_booking_confirmation(booking)` - When booking confirmed
- `send_slot_reminder(booking)` - 24-hour reminder
- `send_queue_update(counter)` - Queue status updates
- `send_system_alert(users, title, message)` - System alerts

### AnalyticsService
Provides analytics and reporting

**Methods:**
- `update_queue_analytics(queue)` - Update daily analytics
- `get_daily_report(queue, date=None)` - Get queue daily report
- `get_branch_daily_report(branch, date=None)` - Branch aggregated report
- `get_service_analytics(service, start_date=None, end_date=None)` - Service analytics

## 🔒 Security & Validation

### Model-Level Validation
- `limit_choices_to` for foreign keys (role-based)
- `clean()` methods for business rule validation
- Validators (MinValueValidator, MaxValueValidator)

### Overbooking Prevention
```python
# In SlotBookingService.create_booking()
if slot.is_fully_booked:
    raise ValueError("This slot is fully booked")
```

### Token Generation Prevents Duplicates
```python
token_number = TokenService.generate_token_number(counter)
# Format: CXXXYYMMDD0001 (unique per day per counter)
```

## 📊 Django Admin Customization

**Features:**
- Colored status badges
- Inline editing for related models
- Date hierarchy for time-based models
- Search and filtering on relevant fields
- Read-only calculations (metrics, analytics)
- Collapsible fieldsets for organization
- Custom admin actions for bulk operations

**Customizations:**
- UserRoleAdmin - Role management
- BankAdmin - Multi-bank support
- BranchAdmin - Branch management with counters
- ServiceAdmin - Service configuration
- CounterAdmin - Counter staff assignment
- SlotAdmin - Slot management with capacity
- SlotBookingAdmin - Booking tracking
- QueueAdmin - Queue metrics
- TokenAdmin - Token lifecycle with metrics
- QueueAnalyticsAdmin - Analytics visualization
- NotificationAdmin - User notifications
- AuditLogAdmin - Compliance tracking

## 🔄 Workflow Examples

### Create Token Workflow
```python
from queueapp.services import TokenService, NotificationService

# 1. Get queue
queue = Queue.objects.get(queue_id='Q001')

# 2. Create token
token = TokenService.create_token(
    queue=queue,
    customer=request.user,
    priority=1  # Normal priority
)

# 3. Token automatically logged in AuditLog
# 4. Token status = 'generated'
```

### Slot Booking Workflow
```python
from queueapp.services import SlotBookingService

# 1. Get available slots
slots = SlotBookingService.get_available_slots(
    service=service,
    branch=branch,
    days_ahead=7
)

# 2. Create booking
booking = SlotBookingService.create_booking(
    user=request.user,
    slot=slots.first(),
    service=service,
    notes="Regular checkup"
)

# 3. Slot capacity automatically updated
# 4. Confirmation notification sent
# 5. Booking logged in AuditLog
```

### Call & Serve Token Workflow
```python
from queueapp.services import TokenService, AnalyticsService

# 1. Call token
token = TokenService.call_token(token)  # Status: called
# Notification sent to customer

# 2. Start service
token = TokenService.start_service(token, staff_member)  # Status: serving

# 3. Complete service
token = TokenService.complete_service(token)  # Status: completed
# Analytics updated for the day
```

## 📈 Analytics & Reporting

**Daily Analytics Update:**
```python
AnalyticsService.update_queue_analytics(queue)

# Creates/updates QueueAnalytics for today:
# - total_tokens
# - served_tokens (completed)
# - cancelled_tokens
# - no_show_tokens
# - avg_wait_time
# - avg_service_time
# - peak_hour
# - max_queue_length
```

**Branch Report:**
```python
report = AnalyticsService.get_branch_daily_report(branch)
# Returns aggregated metrics for all queues in branch
```

## 🔑 Key Features Implemented

✅ **Multi-Bank Support** - Bank and Branch models with hierarchy
✅ **Multi-Counter Management** - Counter-to-Service relationship
✅ **Slot Booking System** - Appointments with overbooking prevention
✅ **Token Management** - Full lifecycle from generation to completion
✅ **Priority Queue** - 4-level priority system (Normal, Senior/PWD, VIP, Emergency)
✅ **Real-Time Queue Status** - Current wait times and queue length
✅ **Daily Analytics** - Comprehensive performance metrics
✅ **Notifications** - Multi-type notification system
✅ **Audit Logging** - Compliance and debugging trail
✅ **Role-Based Access** - 5 user roles with permission model
✅ **Clean Architecture** - Services layer separation
✅ **Admin Customization** - Professional Django admin interface

## 🚀 Next Steps

1. **Create Migrations:**
   ```bash
   python manage.py makemigrations queueapp
   python manage.py migrate
   ```

2. **Create API Views** (in views.py and api.py):
   - Token generation endpoints
   - Slot booking endpoints
   - Queue status endpoints
   - Analytics endpoints

3. **Implement Permissions:**
   - Role-based view access
   - Booking validation
   - Token operation restrictions

4. **Add Tests:**
   - Model tests
   - Service tests
   - API tests
   - Permission tests

5. **Scheduled Tasks:**
   - Daily analytics calculation
   - Booking reminders (SlotBookingService.send_reminders())
   - Old notification cleanup

## 📚 Best Practices Applied

✓ Single Responsibility Principle - Services handle business logic
✓ DRY - Reusable service methods
✓ Clean Code - Clear naming, docstrings
✓ Validation - Model and service-level validation
✓ Indexing - Database indexes for performance
✓ Audit Trail - All operations logged
✓ Error Handling - Meaningful exceptions
✓ Documentation - Comprehensive docstrings
✓ Admin UX - User-friendly interface
✓ Scalability - Designed for multi-branch expansion

## 🔧 Configuration

**Settings to add to settings.py:**
```python
# If using Celery for async tasks
CELERY_BROKER_URL = 'redis://localhost:6379'
CELERY_RESULT_BACKEND = 'redis://localhost:6379'

# Notification settings
NOTIFICATION_ENABLED = True
SEND_EMAIL_NOTIFICATIONS = True
SEND_SMS_NOTIFICATIONS = False  # Configure with Twilio if needed

# Queue settings
TOKEN_EXPIRY_HOURS = 4
SLOT_REMINDER_HOURS = 24
```

## 📝 Next Phase - Real-Time Features

Future enhancements:
- WebSocket integration for real-time token updates
- Queue display systems (public displays)
- Mobile app API
- SMS/Email notifications
- Performance dashboards
