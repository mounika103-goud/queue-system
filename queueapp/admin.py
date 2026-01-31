from django.contrib import admin
from .models import UserRole, Counter, Queue, Token, QueueAnalytics, Notification

@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_active', 'created_at']
    list_filter = ['role', 'is_active']
    search_fields = ['user__username', 'user__email']


@admin.register(Counter)
class CounterAdmin(admin.ModelAdmin):
    list_display = ['counter_id', 'name', 'status', 'manager', 'is_active']
    list_filter = ['status', 'is_active']
    search_fields = ['counter_id', 'name']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    list_display = ['queue_id', 'service_type', 'counter', 'is_active', 'current_wait_time']
    list_filter = ['service_type', 'is_active', 'created_at']
    search_fields = ['queue_id', 'service_type']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Token)
class TokenAdmin(admin.ModelAdmin):
    list_display = ['token_number', 'queue', 'customer', 'status', 'priority', 'generated_at']
    list_filter = ['status', 'priority', 'generated_at']
    search_fields = ['token_number', 'customer__username']
    readonly_fields = ['generated_at', 'called_at', 'service_started_at', 'service_ended_at']


@admin.register(QueueAnalytics)
class QueueAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'queue', 'total_tokens', 'served_tokens', 'avg_wait_time']
    list_filter = ['date', 'queue']
    search_fields = ['queue__queue_id']
    fields = ['date', 'queue', 'total_tokens', 'served_tokens', 'cancelled_tokens', 
              'no_show_tokens', 'avg_wait_time', 'avg_service_time', 'peak_hour']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'title']
    readonly_fields = ['created_at']
