from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator

class UserRole(models.Model):
    """Define user roles in the system"""
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('staff', 'Staff Member'),
        ('counter_manager', 'Counter Manager'),
        ('admin', 'Administrator'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='role')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='customer')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "User Role"
        verbose_name_plural = "User Roles"
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Counter(models.Model):
    """Physical or Virtual counter at the bank"""
    COUNTER_STATUS = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('maintenance', 'Under Maintenance'),
    ]
    
    counter_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100, default="Counter")
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=COUNTER_STATUS, default='active')
    manager = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_counters', limit_choices_to={'role__role': 'counter_manager'})
    current_staff = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='working_counter')
    staff_member = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_counter')
    
    # Service types handled at this counter
    service_types = models.CharField(max_length=255, help_text="Comma-separated service types", blank=True)
    
    # Counter status
    is_active = models.BooleanField(default=True)
    is_online = models.BooleanField(default=False)
    is_busy = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Counter"
        verbose_name_plural = "Counters"
    
    def __str__(self):
        return f"{self.name} ({self.counter_id})"


class Queue(models.Model):
    """Queue management for a specific service"""
    SERVICE_TYPES = [
        ('deposits', 'Deposits'),
        ('withdrawals', 'Withdrawals'),
        ('loans', 'Loan Services'),
        ('account_opening', 'Account Opening'),
        ('general', 'General Inquiry'),
    ]
    
    queue_id = models.CharField(max_length=50, unique=True)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPES, default='general')
    counter = models.ForeignKey(Counter, on_delete=models.CASCADE, related_name='queues')
    is_active = models.BooleanField(default=True)
    
    # Queue statistics
    average_service_time = models.IntegerField(default=5, validators=[MinValueValidator(1)], help_text="In minutes")
    current_wait_time = models.IntegerField(default=0, help_text="In minutes")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Queue"
        verbose_name_plural = "Queues"
        unique_together = ('counter', 'service_type')
    
    def __str__(self):
        return f"{self.service_type} - {self.counter.counter_name}"


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
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='tokens')
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='user_tokens')
    counter = models.ForeignKey(Counter, on_delete=models.SET_NULL, null=True, blank=True, related_name='tokens')
    
    status = models.CharField(max_length=20, choices=TOKEN_STATUS, default='generated')
    priority = models.IntegerField(choices=PRIORITY_LEVELS, default=1)
    
    # Timestamps
    generated_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
    called_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    served_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='served_tokens')
    service_started_at = models.DateTimeField(null=True, blank=True)
    service_ended_at = models.DateTimeField(null=True, blank=True)
    
    # Estimated wait time when token was generated
    estimated_wait_time = models.IntegerField(null=True, blank=True, help_text="In minutes")
    waiting_time = models.IntegerField(null=True, blank=True, help_text="Actual wait time in minutes")
    service_duration = models.IntegerField(null=True, blank=True, help_text="Service duration in minutes")
    
    # Additional fields
    cancellation_reason = models.CharField(max_length=255, blank=True)
    skip_count = models.IntegerField(default=0)
    customer_notes = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Token"
        verbose_name_plural = "Tokens"
        ordering = ['-generated_at']
    
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
        """Calculate service time in minutes"""
        if self.service_ended_at:
            return int((self.service_ended_at - self.service_started_at).total_seconds() / 60)
        return None


class QueueAnalytics(models.Model):
    """Store analytics data for reporting and insights"""
    date = models.DateField(auto_now_add=True)
    queue = models.ForeignKey(Queue, on_delete=models.CASCADE, related_name='analytics')
    
    total_tokens = models.IntegerField(default=0)
    served_tokens = models.IntegerField(default=0)
    cancelled_tokens = models.IntegerField(default=0)
    no_show_tokens = models.IntegerField(default=0)
    
    avg_wait_time = models.IntegerField(null=True, blank=True, help_text="In minutes")
    avg_service_time = models.IntegerField(null=True, blank=True, help_text="In minutes")
    peak_hour = models.IntegerField(null=True, blank=True, help_text="Hour of day 0-23")
    
    class Meta:
        verbose_name = "Queue Analytics"
        verbose_name_plural = "Queue Analytics"
        unique_together = ('date', 'queue')
    
    def __str__(self):
        return f"{self.queue.service_type} - {self.date}"


class Notification(models.Model):
    """Notifications for customers and staff"""
    NOTIFICATION_TYPES = [
        ('token_called', 'Token Called'),
        ('queue_update', 'Queue Update'),
        ('system_alert', 'System Alert'),
        ('service_alert', 'Service Alert'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    token = models.ForeignKey(Token, on_delete=models.SET_NULL, null=True, blank=True, related_name='notifications')
    
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.notification_type} - {self.user.username}"
