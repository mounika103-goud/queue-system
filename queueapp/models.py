from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
# Removed unused imports: datetime, timedelta, random, string


# ============================================================================
# USER & ROLE MANAGEMENT
# ============================================================================

class UserRole(models.Model):
    """Define user roles in the system"""
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('staff', 'Staff Member'),
        ('counter_manager', 'Counter Manager'),
        ('branch_manager', 'Branch Manager'),
        ('admin', 'Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
        indexes = [models.Index(fields=['role', 'is_active'])]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"
    
    @classmethod
    def get_user_role(cls, user):
        """Get role for a user"""
        try:
            return cls.objects.get(user=user).role
        except cls.DoesNotExist:
            return None


# ============================================================================
# BANKING HIERARCHY
# ============================================================================

class Bank(models.Model):
    """Bank in the system"""
    BANK_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('under_maintenance', 'Under Maintenance'),
    ]
    
    bank_code = models.CharField(
        max_length=20, 
        unique=True, 
        help_text="Bank IFSC code prefix"
    )
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=30, choices=BANK_STATUS, default='active')
    
    # Contact information
    phone_number = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    
    # Admin for this bank
    admin = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_banks',
        limit_choices_to={'role__role': 'admin'}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Bank"
        verbose_name_plural = "Banks"
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.bank_code})"


class Branch(models.Model):
    """Bank branch"""
    BRANCH_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('closed', 'Closed'),
    ]
    
    bank = models.ForeignKey(Bank, on_delete=models.CASCADE, related_name='branches')
    branch_code = models.CharField(max_length=20)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=BRANCH_STATUS, default='active')
    
    # Location information
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    
    # Operating hours
    opening_time = models.TimeField(default='09:00')
    closing_time = models.TimeField(default='17:00')
    
    # Manager
    manager = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_branches',
        limit_choices_to={'role__role': 'branch_manager'}
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Branch"
        verbose_name_plural = "Branches"
        unique_together = ('bank', 'branch_code')
        ordering = ['bank', 'name']
    
    def __str__(self):
        return f"{self.bank.name} - {self.name}"
    
    def is_open(self):
        """Check if branch is currently open"""
        now = timezone.now().time()
        return self.opening_time <= now <= self.closing_time
    
    def get_active_counters(self):
        """Get all active counters at this branch"""
        return self.counters.filter(status='active', is_active=True)


# ============================================================================
# SERVICES & COUNTERS
# ============================================================================

class Service(models.Model):
    """Banking services offered"""
    SERVICE_TYPES = [
        ('deposits', 'Deposits'),
        ('withdrawals', 'Withdrawals'),
        ('loans', 'Loan Services'),
        ('account_opening', 'Account Opening'),
        ('account_maintenance', 'Account Maintenance'),
        ('cash_counter', 'Cash Counter'),
        ('general_inquiry', 'General Inquiry'),
        ('foreign_exchange', 'Foreign Exchange'),
    ]
    
    service_code = models.CharField(max_length=20, unique=True)
    service_type = models.CharField(max_length=30, choices=SERVICE_TYPES)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    
    # Time estimates
    average_service_time = models.IntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(120)],
        help_text="Estimated service time in minutes"
    )
    
    # Configuration
    is_active = models.BooleanField(default=True)
    requires_appointment = models.BooleanField(default=False)
    max_queue_size = models.IntegerField(default=50, validators=[MinValueValidator(1)])
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ['service_type', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.service_code})"


class Counter(models.Model):
    """Physical or Virtual counter at a branch"""
    COUNTER_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, related_name='counters', null=True, blank=True)
    counter_id = models.CharField(max_length=50)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=COUNTER_STATUS, default='active')
    
    # Services handled at this counter
    service = models.ForeignKey(
        Service, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='counters'
    )
    
    # Staff assignment
    manager = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='managed_counters',
        limit_choices_to={'role__role': 'counter_manager'}
    )
    staff_member = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_counter',
        limit_choices_to={'role__role': 'staff'}
    )
    
    # Counter status
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    is_busy = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Counter"
        verbose_name_plural = "Counters"
        unique_together = ('branch', 'counter_id')
        ordering = ['branch', 'counter_id']
    
    def __str__(self):
        return f"{self.name} - {self.branch.name}"
    
    def get_current_token(self):
        """Get currently serving token"""
        return self.tokens.filter(status='serving').first()
    
    def get_waiting_tokens(self):
        """Get tokens waiting at this counter"""
        return self.tokens.filter(status='waiting').order_by('priority', 'generated_at')


# ============================================================================
# SLOT MANAGEMENT
# ============================================================================

class Slot(models.Model):
    """Available time slots for appointments"""
    SLOT_STATUS = [
        ('available', 'Available'),
        ('partially_booked', 'Partially Booked'),
        ('fully_booked', 'Fully Booked'),
        ('closed', 'Closed'),
    ]
    
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE, related_name='slots')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='slots')
    slot_date = models.DateField()
    slot_start_time = models.TimeField()
    slot_end_time = models.TimeField()
    
    # Capacity management
    max_capacity = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(100)]
    )
    current_bookings = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    status = models.CharField(max_length=20, choices=SLOT_STATUS, default='available')
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Slot"
        verbose_name_plural = "Slots"
        unique_together = ('counter', 'slot_date', 'slot_start_time')
        ordering = ['slot_date', 'slot_start_time']
        indexes = [
            models.Index(fields=['slot_date', 'status']),
            models.Index(fields=['counter', 'slot_date']),
        ]
    
    def __str__(self):
        return f"{self.service.name} - {self.slot_date} {self.slot_start_time}"
    
    def clean(self):
        """Validate slot times"""
        if self.slot_start_time >= self.slot_end_time:
            raise ValidationError("Slot start time must be before end time")
        if self.current_bookings > self.max_capacity:
            raise ValidationError("Current bookings cannot exceed max capacity")
    
    def save(self, *args, **kwargs):
        """Auto-update status based on bookings"""
        self.clean()
        if self.current_bookings >= self.max_capacity:
            self.status = 'fully_booked'
        elif self.current_bookings > 0:
            self.status = 'partially_booked'
        else:
            self.status = 'available'
        super().save(*args, **kwargs)
    
    @property
    def available_slots(self):
        """Get number of available slots"""
        return self.max_capacity - self.current_bookings
    
    @property
    def is_fully_booked(self):
        """Check if slot is fully booked"""
        return self.current_bookings >= self.max_capacity


class SlotBooking(models.Model):
    """Customer slot bookings"""
    BOOKING_STATUS = [
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
        ('no_show', 'No Show'),
    ]
    
    booking_id = models.CharField(max_length=50, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='slot_bookings')
    slot = models.ForeignKey(Slot, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=BOOKING_STATUS, default='confirmed')
    
    # Optional fields
    customer_notes = models.TextField(blank=True)
    cancellation_reason = models.CharField(max_length=255, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    is_reminder_sent = models.BooleanField(default=False)
    reminder_sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Slot Booking"
        verbose_name_plural = "Slot Bookings"
        unique_together = ('user', 'slot')
        ordering = ['-booking_date']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['slot', 'status']),
            models.Index(fields=['booking_date']),
        ]
    
    def __str__(self):
        return f"Booking {self.booking_id}"
    
    def clean(self):
        """Validate booking"""
        if self.slot.is_fully_booked:
            raise ValidationError("This slot is fully booked")
        if self.slot.slot_date < timezone.now().date():
            raise ValidationError("Cannot book slots in the past")
    
    def cancel(self, reason=""):
        """Cancel a booking"""
        if self.status != 'confirmed':
            raise ValidationError("Only confirmed bookings can be cancelled")
        
        self.status = 'cancelled'
        self.cancellation_reason = reason
        self.cancelled_at = timezone.now()
        
        # Decrease slot bookings
        self.slot.current_bookings -= 1
        self.slot.save()
        
        self.save()


# ============================================================================
# TOKEN & QUEUE MANAGEMENT
# ============================================================================

class Queue(models.Model):
    """Queue management for a specific service at a counter"""
    
    queue_id = models.CharField(max_length=50, unique=True)
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE, related_name='queues')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='queues')
    is_active = models.BooleanField(default=True)
    
    # Queue statistics
    average_service_time = models.IntegerField(
        default=5, 
        validators=[MinValueValidator(1)], 
        help_text="In minutes"
    )
    current_wait_time = models.IntegerField(default=0, help_text="In minutes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Queue"
        verbose_name_plural = "Queues"
        unique_together = ('counter', 'service')
        ordering = ['counter', 'service']
    
    def __str__(self):
        return f"{self.service.name} - {self.counter.name}"
    
    def get_waiting_count(self):
        """Get count of waiting tokens"""
        return self.tokens.filter(status='waiting').count()
    
    def get_active_tokens(self):
        """Get all active tokens in queue"""
        return self.tokens.filter(status__in=['waiting', 'called', 'serving'])


class Token(models.Model):
    """Token issued to customers"""
    TOKEN_STATUS = [
        ('generated', 'Generated'),
        ('waiting', 'Waiting'),
        ('called', 'Called'),
        ('serving', 'Being Served'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    PRIORITY_LEVELS = [
        (1, 'Normal'),
        (2, 'Senior Citizen/PWD'),
        (3, 'VIP'),
        (4, 'Emergency'),
    ]
    
    token_number = models.CharField(max_length=50, unique=True)
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name='tokens')
    customer = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='tokens',
        limit_choices_to={'role__role': 'customer'}
    )
    counter = models.ForeignKey(
        Counter, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='tokens'
    )
    
    status = models.CharField(max_length=20, choices=TOKEN_STATUS, default='generated')
    priority = models.IntegerField(choices=PRIORITY_LEVELS, default=1)
    
    # Timestamps
    generated_at = models.DateTimeField(auto_now_add=True)
    called_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    # Service tracking
    served_by = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='served_tokens',
        limit_choices_to={'role__role': 'staff'}
    )
    service_started_at = models.DateTimeField(null=True, blank=True)
    service_ended_at = models.DateTimeField(null=True, blank=True)
    
    # Timing metrics
    estimated_wait_time = models.IntegerField(null=True, blank=True, help_text="In minutes")
    waiting_time = models.IntegerField(null=True, blank=True, help_text="Actual wait time in minutes")
    
    # Additional fields
    cancellation_reason = models.CharField(max_length=255, blank=True)
    skip_count = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    customer_notes = models.TextField(blank=True, null=True)
    
    # Slot reference (optional)
    slot_booking = models.ForeignKey(
        SlotBooking, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='token'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Token"
        verbose_name_plural = "Tokens"
        ordering = ['-generated_at']
        indexes = [
            models.Index(fields=['status', 'queue']),
            models.Index(fields=['customer', 'status']),
            models.Index(fields=['generated_at']),
        ]
    
    def __str__(self):
        return f"Token {self.token_number}"
    
    @property
    def wait_duration(self):
        """Calculate actual wait time in minutes"""
        if self.called_at:
            return int((self.called_at - self.generated_at).total_seconds() / 60)
        return None
    
    @property
    def service_duration(self):
        """Calculate service duration in minutes"""
        if self.service_started_at and self.service_ended_at:
            return int((self.service_ended_at - self.service_started_at).total_seconds() / 60)
        return None
    
    def get_priority_display_full(self):
        """Get full priority display with details"""
        priority_details = {
            1: "Normal Priority",
            2: "Senior Citizen/PWD",
            3: "VIP Customer",
            4: "Emergency Service"
        }
        return priority_details.get(self.priority, "Unknown")


# ============================================================================
# ANALYTICS & REPORTING
# ============================================================================

class QueueAnalytics(models.Model):
    """Store analytics data for reporting and insights"""
    date = models.DateField()
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name='analytics')
    
    total_tokens = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    served_tokens = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    cancelled_tokens = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    no_show_tokens = models.IntegerField(default=0, validators=[MinValueValidator(0)])
    
    avg_wait_time = models.IntegerField(null=True, blank=True, help_text="In minutes")
    avg_service_time = models.IntegerField(null=True, blank=True, help_text="In minutes")
    peak_hour = models.IntegerField(null=True, blank=True, help_text="Hour of day 0-23")
    max_queue_length = models.IntegerField(default=0, help_text="Peak queue length")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Queue Analytics"
        verbose_name_plural = "Queue Analytics"
        unique_together = ('date', 'queue')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['queue', 'date']),
        ]
    
    def __str__(self):
        return f"{self.queue.service.name} - {self.date}"
    
    @property
    def served_percentage(self):
        """Calculate percentage of served tokens"""
        if self.total_tokens == 0:
            return 0
        return (self.served_tokens / self.total_tokens) * 100


# ============================================================================
# NOTIFICATIONS
# ============================================================================

class Notification(models.Model):
    """Notifications for customers and staff"""
    NOTIFICATION_TYPES = [
        ('token_called', 'Token Called'),
        ('token_confirmed', 'Token Confirmed'),
        ('slot_reminder', 'Slot Reminder'),
        ('queue_update', 'Queue Update'),
        ('system_alert', 'System Alert'),
        ('service_alert', 'Service Alert'),
        ('booking_confirmation', 'Booking Confirmation'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    
    # References
    token = models.ForeignKey(
        Token, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='notifications'
    )
    slot_booking = models.ForeignKey(
        SlotBooking, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='notifications'
    )
    
    # Status tracking
    is_read = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.notification_type} - {self.user.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()


# ============================================================================
# AUDIT & COMPLIANCE
# ============================================================================

class AuditLog(models.Model):
    """Audit log for compliance and debugging"""
    ACTION_TYPES = [
        ('token_generated', 'Token Generated'),
        ('token_called', 'Token Called'),
        ('token_served', 'Token Served'),
        ('booking_created', 'Booking Created'),
        ('booking_cancelled', 'Booking Cancelled'),
        ('counter_activated', 'Counter Activated'),
        ('counter_deactivated', 'Counter Deactivated'),
        ('staff_assigned', 'Staff Assigned'),
        ('other', 'Other'),
    ]
    
    action_type = models.CharField(max_length=30, choices=ACTION_TYPES)
    description = models.TextField()
    user = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='audit_logs'
    )
    
    # References
    token = models.ForeignKey(
        Token, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='audit_logs'
    )
    slot_booking = models.ForeignKey(
        SlotBooking, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='audit_logs'
    )
    
    # Additional data
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=500, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Audit Log"
        verbose_name_plural = "Audit Logs"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action_type', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.action_type} - {self.created_at}"
