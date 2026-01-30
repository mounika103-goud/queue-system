"""
Django Admin configuration for Smart Banking Queue Management System.

Customizes the admin interface with proper display, filtering, search,
and actions for all models.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.db.models import Count, Avg
from datetime import timedelta
from django.utils import timezone

from .models import (
    UserRole, Bank, Branch, Service, Counter, Slot, SlotBooking,
    Queue, Token, QueueAnalytics, Notification, AuditLog
)


# ============================================================================
# DISPLAY UTILITIES
# ============================================================================

def get_status_badge(status, status_map):
    """Generate colored status badge"""
    colors = {
        'active': '#28a745',
        'inactive': '#6c757d',
        'confirmed': '#28a745',
        'cancelled': '#dc3545',
        'completed': '#17a2b8',
        'waiting': '#ffc107',
        'called': '#fd7e14',
        'serving': '#007bff',
        'available': '#28a745',
        'partially_booked': '#ffc107',
        'fully_booked': '#dc3545',
    }
    
    display_text = status_map.get(status, status)
    color = colors.get(status, '#6c757d')
    
    return format_html(
        '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
        color, display_text
    )


# ============================================================================
# INLINES
# ============================================================================

class CounterInline(admin.TabularInline):
    """Inline for counters in branch admin"""
    model = Counter
    extra = 1
    fields = ('counter_id', 'name', 'service', 'status', 'staff_member', 'is_active')
    readonly_fields = ('created_at',)


class SlotInline(admin.TabularInline):
    """Inline for slots in counter admin"""
    model = Slot
    extra = 1
    fields = ('service', 'slot_date', 'slot_start_time', 'slot_end_time', 'max_capacity', 'current_bookings')


class QueueInline(admin.TabularInline):
    """Inline for queues in counter admin"""
    model = Queue
    extra = 1
    fields = ('service', 'average_service_time', 'is_active')


# ============================================================================
# USER ROLE ADMIN
# ============================================================================

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """Admin for user roles"""
    list_display = ('user', 'get_role_display', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Role Configuration', {
            'fields': ('role', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# BANK ADMIN
# ============================================================================

@admin.register(Bank)
class BankAdmin(admin.ModelAdmin):
    """Admin for banks"""
    list_display = ('name', 'bank_code', 'get_status', 'get_branch_count', 'admin', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('name', 'bank_code', 'email')
    readonly_fields = ('created_at', 'updated_at', 'get_branch_count')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'bank_code', 'description')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone_number')
        }),
        ('Administration', {
            'fields': ('admin', 'status')
        }),
        ('Statistics', {
            'fields': ('get_branch_count',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status(self, obj):
        """Display status with badge"""
        status_map = {'active': 'Active', 'inactive': 'Inactive', 'under_maintenance': 'Under Maintenance'}
        return get_status_badge(obj.status, status_map)
    get_status.short_description = 'Status'
    
    def get_branch_count(self, obj):
        """Count branches for this bank"""
        return obj.branches.count()
    get_branch_count.short_description = 'Total Branches'


# ============================================================================
# BRANCH ADMIN
# ============================================================================

@admin.register(Branch)
class BranchAdmin(admin.ModelAdmin):
    """Admin for branches"""
    list_display = ('name', 'bank', 'branch_code', 'city', 'get_status', 'manager', 'get_is_open')
    list_filter = ('status', 'bank', 'city', 'state')
    search_fields = ('name', 'branch_code', 'city', 'address')
    readonly_fields = ('created_at', 'updated_at', 'get_is_open')
    inlines = [CounterInline]
    
    fieldsets = (
        ('Bank Information', {
            'fields': ('bank', 'branch_code')
        }),
        ('Branch Details', {
            'fields': ('name', 'description', 'status')
        }),
        ('Location', {
            'fields': ('address', 'city', 'state', 'postal_code')
        }),
        ('Operating Hours', {
            'fields': ('opening_time', 'closing_time', 'get_is_open')
        }),
        ('Management', {
            'fields': ('manager',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status(self, obj):
        """Display status with badge"""
        status_map = {'active': 'Active', 'inactive': 'Inactive', 'closed': 'Closed'}
        return get_status_badge(obj.status, status_map)
    get_status.short_description = 'Status'
    
    def get_is_open(self, obj):
        """Display if branch is currently open"""
        is_open = obj.is_open()
        color = '#28a745' if is_open else '#dc3545'
        text = 'Open Now' if is_open else 'Closed Now'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, text
        )
    get_is_open.short_description = 'Currently Open'


# ============================================================================
# SERVICE ADMIN
# ============================================================================

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    """Admin for services"""
    list_display = ('name', 'service_code', 'service_type', 'average_service_time', 'is_active', 'requires_appointment')
    list_filter = ('service_type', 'is_active', 'requires_appointment', 'created_at')
    search_fields = ('name', 'service_code', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Service Information', {
            'fields': ('name', 'service_code', 'service_type', 'description')
        }),
        ('Configuration', {
            'fields': ('average_service_time', 'max_queue_size', 'is_active', 'requires_appointment')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# COUNTER ADMIN
# ============================================================================

@admin.register(Counter)
class CounterAdmin(admin.ModelAdmin):
    """Admin for counters"""
    list_display = ('name', 'counter_id', 'branch', 'service', 'get_status', 'staff_member', 'is_busy')
    list_filter = ('status', 'is_active', 'is_busy', 'branch', 'service')
    search_fields = ('name', 'counter_id', 'description')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [QueueInline, SlotInline]
    
    fieldsets = (
        ('Counter Information', {
            'fields': ('counter_id', 'name', 'branch', 'description')
        }),
        ('Services', {
            'fields': ('service',)
        }),
        ('Staff Assignment', {
            'fields': ('manager', 'staff_member')
        }),
        ('Status', {
            'fields': ('status', 'is_active', 'is_online', 'is_busy')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status(self, obj):
        """Display status with badge"""
        status_map = {'active': 'Active', 'inactive': 'Inactive', 'maintenance': 'Under Maintenance'}
        return get_status_badge(obj.status, status_map)
    get_status.short_description = 'Status'


# ============================================================================
# SLOT ADMIN
# ============================================================================

@admin.register(Slot)
class SlotAdmin(admin.ModelAdmin):
    """Admin for slots"""
    list_display = ('service', 'counter', 'slot_date', 'slot_start_time', 'get_status', 'get_capacity')
    list_filter = ('status', 'service', 'counter', 'slot_date')
    search_fields = ('service__name', 'counter__name')
    readonly_fields = ('created_at', 'updated_at', 'get_available_slots')
    date_hierarchy = 'slot_date'
    
    fieldsets = (
        ('Slot Information', {
            'fields': ('counter', 'service', 'slot_date')
        }),
        ('Time Range', {
            'fields': ('slot_start_time', 'slot_end_time')
        }),
        ('Capacity', {
            'fields': ('max_capacity', 'current_bookings', 'get_available_slots')
        }),
        ('Status', {
            'fields': ('status', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status(self, obj):
        """Display status with badge"""
        status_map = {
            'available': 'Available',
            'partially_booked': 'Partially Booked',
            'fully_booked': 'Fully Booked',
            'closed': 'Closed'
        }
        return get_status_badge(obj.status, status_map)
    get_status.short_description = 'Status'
    
    def get_capacity(self, obj):
        """Display capacity information"""
        return f"{obj.current_bookings}/{obj.max_capacity}"
    get_capacity.short_description = 'Bookings/Capacity'
    
    def get_available_slots(self, obj):
        """Display available slots count"""
        return obj.available_slots
    get_available_slots.short_description = 'Available Slots'


# ============================================================================
# SLOT BOOKING ADMIN
# ============================================================================

@admin.register(SlotBooking)
class SlotBookingAdmin(admin.ModelAdmin):
    """Admin for slot bookings"""
    list_display = ('booking_id', 'user', 'service', 'slot', 'get_status', 'booking_date')
    list_filter = ('status', 'service', 'booking_date')
    search_fields = ('booking_id', 'user__username', 'service__name')
    readonly_fields = ('booking_id', 'booking_date', 'created_at', 'updated_at')
    date_hierarchy = 'booking_date'
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking_id', 'user', 'service')
        }),
        ('Slot Details', {
            'fields': ('slot',)
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Notes', {
            'fields': ('customer_notes', 'cancellation_reason')
        }),
        ('Reminder', {
            'fields': ('is_reminder_sent', 'reminder_sent_at')
        }),
        ('Timestamps', {
            'fields': ('booking_date', 'cancelled_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status(self, obj):
        """Display status with badge"""
        status_map = {'confirmed': 'Confirmed', 'cancelled': 'Cancelled', 'completed': 'Completed', 'no_show': 'No Show'}
        return get_status_badge(obj.status, status_map)
    get_status.short_description = 'Status'


# ============================================================================
# QUEUE ADMIN
# ============================================================================

@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    """Admin for queues"""
    list_display = ('queue_id', 'service', 'counter', 'get_waiting_count', 'average_service_time', 'is_active')
    list_filter = ('service', 'counter', 'is_active')
    search_fields = ('queue_id', 'service__name', 'counter__name')
    readonly_fields = ('created_at', 'updated_at', 'get_waiting_count', 'get_average_metrics')
    
    fieldsets = (
        ('Queue Information', {
            'fields': ('queue_id', 'counter', 'service')
        }),
        ('Settings', {
            'fields': ('average_service_time', 'current_wait_time', 'is_active')
        }),
        ('Metrics', {
            'fields': ('get_waiting_count', 'get_average_metrics'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_waiting_count(self, obj):
        """Display count of waiting tokens"""
        return obj.get_waiting_count()
    get_waiting_count.short_description = 'Waiting Tokens'
    
    def get_average_metrics(self, obj):
        """Display average metrics"""
        avg_wait = obj.tokens.filter(status='completed').aggregate(Avg('waiting_time'))['waiting_time__avg']
        return f"Avg Wait: {int(avg_wait) if avg_wait else 0} min"
    get_average_metrics.short_description = 'Average Metrics'


# ============================================================================
# TOKEN ADMIN
# ============================================================================

@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    """Admin for tokens"""
    list_display = ('token_number', 'queue', 'customer', 'get_status', 'priority', 'generated_at')
    list_filter = ('status', 'priority', 'generated_at', 'queue')
    search_fields = ('token_number', 'customer__username', 'queue__queue_id')
    readonly_fields = ('token_number', 'generated_at', 'created_at', 'updated_at', 'get_wait_time', 'get_service_time')
    date_hierarchy = 'generated_at'
    
    fieldsets = (
        ('Token Information', {
            'fields': ('token_number', 'queue', 'customer', 'counter')
        }),
        ('Status', {
            'fields': ('status', 'priority')
        }),
        ('Service Details', {
            'fields': ('served_by', 'service_started_at', 'service_ended_at')
        }),
        ('Timing', {
            'fields': ('generated_at', 'called_at', 'completed_at', 'cancelled_at'),
            'classes': ('collapse',)
        }),
        ('Metrics', {
            'fields': ('estimated_wait_time', 'waiting_time', 'service_duration', 'get_wait_time', 'get_service_time'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('skip_count', 'customer_notes', 'cancellation_reason', 'slot_booking')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_status(self, obj):
        """Display status with badge"""
        status_map = {
            'generated': 'Generated',
            'waiting': 'Waiting',
            'called': 'Called',
            'serving': 'Being Served',
            'completed': 'Completed',
            'cancelled': 'Cancelled',
            'no_show': 'No Show'
        }
        return get_status_badge(obj.status, status_map)
    get_status.short_description = 'Status'
    
    def get_wait_time(self, obj):
        """Display actual wait time"""
        return f"{obj.wait_duration} min" if obj.wait_duration else "N/A"
    get_wait_time.short_description = 'Actual Wait Time'
    
    def get_service_time(self, obj):
        """Display actual service time"""
        return f"{obj.service_duration} min" if obj.service_duration else "N/A"
    get_service_time.short_description = 'Service Duration'


# ============================================================================
# QUEUE ANALYTICS ADMIN
# ============================================================================

@admin.register(QueueAnalytics)
class QueueAnalyticsAdmin(admin.ModelAdmin):
    """Admin for queue analytics"""
    list_display = ('date', 'queue', 'total_tokens', 'served_tokens', 'get_service_rate', 'avg_wait_time')
    list_filter = ('date', 'queue')
    search_fields = ('queue__queue_id', 'queue__service__name')
    readonly_fields = ('created_at', 'updated_at', 'get_service_rate')
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Analytics Information', {
            'fields': ('date', 'queue')
        }),
        ('Token Metrics', {
            'fields': ('total_tokens', 'served_tokens', 'cancelled_tokens', 'no_show_tokens', 'get_service_rate')
        }),
        ('Timing Metrics', {
            'fields': ('avg_wait_time', 'avg_service_time', 'peak_hour', 'max_queue_length')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_service_rate(self, obj):
        """Display service completion rate"""
        rate = obj.served_percentage
        color = '#28a745' if rate >= 80 else '#ffc107' if rate >= 60 else '#dc3545'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{:.1f}%</span>',
            color, rate
        )
    get_service_rate.short_description = 'Service Rate'


# ============================================================================
# NOTIFICATION ADMIN
# ============================================================================

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin for notifications"""
    list_display = ('title', 'user', 'notification_type', 'get_is_read', 'created_at')
    list_filter = ('notification_type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'user__username')
    readonly_fields = ('created_at', 'read_at')
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Notification Information', {
            'fields': ('user', 'notification_type')
        }),
        ('Content', {
            'fields': ('title', 'message')
        }),
        ('References', {
            'fields': ('token', 'slot_booking')
        }),
        ('Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_is_read(self, obj):
        """Display read status"""
        status = 'Read' if obj.is_read else 'Unread'
        color = '#6c757d' if obj.is_read else '#007bff'
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color, status
        )
    get_is_read.short_description = 'Read Status'


# ============================================================================
# AUDIT LOG ADMIN
# ============================================================================

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin for audit logs"""
    list_display = ('action_type', 'user', 'description', 'created_at')
    list_filter = ('action_type', 'created_at', 'user')
    search_fields = ('description', 'user__username', 'ip_address')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Audit Information', {
            'fields': ('action_type', 'user')
        }),
        ('Details', {
            'fields': ('description',)
        }),
        ('References', {
            'fields': ('token', 'slot_booking')
        }),
        ('Request Information', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


# ============================================================================
# ADMIN SITE CUSTOMIZATION
# ============================================================================

admin.site.site_header = "Smart Banking Queue Management System"
admin.site.site_title = "Banking Queue Admin"
admin.site.index_title = "Dashboard"
