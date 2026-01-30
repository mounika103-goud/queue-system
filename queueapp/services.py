"""
Business logic services for Smart Banking Queue Management System.

This module contains all the core business logic separated from models and views.
Services handle token generation, slot booking, queue management, and notifications.
"""

from django.utils import timezone
from django.db.models import Q, Count, Avg
from datetime import datetime, timedelta
import random
import string
import uuid

from .models import (
    Token, Queue, Counter, Slot, SlotBooking, Service,
    Notification, AuditLog, QueueAnalytics, Branch
)


# ============================================================================
# TOKEN SERVICE
# ============================================================================

class TokenService:
    """Service for token generation and management"""
    
    @staticmethod
    def generate_token_number(counter):
        """
        Generate a unique token number for a counter.
        Format: COUNTER_CODE-DATE-SEQUENCE
        Example: C001-240315-0001
        """
        today = timezone.now().strftime("%y%m%d")
        today_count = Token.objects.filter(
            counter=counter,
            generated_at__date=timezone.now().date()
        ).count() + 1
        
        counter_code = f"C{counter.branch.bank.bank_code[-3:]}"
        token_number = f"{counter_code}-{today}-{str(today_count).zfill(4)}"
        
        return token_number
    
    @staticmethod
    def create_token(queue, customer, priority=1, from_booking=None):
        """
        Create a new token for a customer.
        
        Args:
            queue: Queue object
            customer: User object (customer)
            priority: Priority level (1-4)
            from_booking: Optional SlotBooking object
            
        Returns:
            Token object
        """
        # Validate queue is active
        if not queue.is_active:
            raise ValueError("Queue is not active")
        
        # Generate token number
        token_number = TokenService.generate_token_number(queue.counter)
        
        # Calculate estimated wait time
        waiting_tokens = queue.get_active_tokens().count()
        avg_service_time = queue.average_service_time
        estimated_wait = waiting_tokens * avg_service_time
        
        # Create token
        token = Token.objects.create(
            token_number=token_number,
            queue=queue,
            customer=customer,
            counter=queue.counter,
            priority=priority,
            estimated_wait_time=estimated_wait,
            slot_booking=from_booking
        )
        
        # Log audit
        AuditLog.objects.create(
            action_type='token_generated',
            description=f"Token {token_number} generated for {customer.username}",
            user=customer,
            token=token
        )
        
        return token
    
    @staticmethod
    def call_token(token):
        """
        Call a token to a counter.
        
        Args:
            token: Token object
            
        Returns:
            Token object
        """
        if token.status not in ['generated', 'waiting']:
            raise ValueError(f"Cannot call token with status: {token.status}")
        
        token.status = 'called'
        token.called_at = timezone.now()
        token.save()
        
        # Create notification
        NotificationService.send_token_called_notification(token)
        
        # Log audit
        AuditLog.objects.create(
            action_type='token_called',
            description=f"Token {token.token_number} called at counter {token.counter.name}",
            user=token.counter.staff_member,
            token=token
        )
        
        return token
    
    @staticmethod
    def start_service(token, staff_member):
        """
        Start serving a token.
        
        Args:
            token: Token object
            staff_member: Staff User object
            
        Returns:
            Token object
        """
        if token.status != 'called':
            raise ValueError(f"Cannot start service for token with status: {token.status}")
        
        token.status = 'serving'
        token.service_started_at = timezone.now()
        token.served_by = staff_member
        token.save()
        
        return token
    
    @staticmethod
    def complete_service(token):
        """
        Complete service for a token.
        
        Args:
            token: Token object
            
        Returns:
            Token object
        """
        if token.status != 'serving':
            raise ValueError(f"Cannot complete service for token with status: {token.status}")
        
        token.status = 'completed'
        token.service_ended_at = timezone.now()
        
        # Calculate actual times
        if token.called_at:
            token.waiting_time = int((token.called_at - token.generated_at).total_seconds() / 60)
        
        if token.service_started_at and token.service_ended_at:
            token.service_duration = int(
                (token.service_ended_at - token.service_started_at).total_seconds() / 60
            )
        
        token.completed_at = timezone.now()
        token.save()
        
        # Update queue analytics
        AnalyticsService.update_queue_analytics(token.queue)
        
        # Log audit
        AuditLog.objects.create(
            action_type='token_served',
            description=f"Token {token.token_number} completed by {token.served_by.username}",
            user=token.served_by,
            token=token
        )
        
        return token
    
    @staticmethod
    def cancel_token(token, reason=""):
        """
        Cancel a token.
        
        Args:
            token: Token object
            reason: Cancellation reason
            
        Returns:
            Token object
        """
        if token.status in ['completed', 'cancelled', 'no_show']:
            raise ValueError(f"Cannot cancel token with status: {token.status}")
        
        token.status = 'cancelled'
        token.cancelled_at = timezone.now()
        token.cancellation_reason = reason
        token.save()
        
        # Log audit
        AuditLog.objects.create(
            action_type='token_called',
            description=f"Token {token.token_number} cancelled - {reason}",
            token=token
        )
        
        return token
    
    @staticmethod
    def mark_no_show(token):
        """
        Mark token as no-show when customer doesn't appear.
        
        Args:
            token: Token object
            
        Returns:
            Token object
        """
        if token.status != 'called':
            raise ValueError(f"Cannot mark no-show for token with status: {token.status}")
        
        token.status = 'no_show'
        token.cancelled_at = timezone.now()
        token.save()
        
        return token


# ============================================================================
# SLOT BOOKING SERVICE
# ============================================================================

class SlotBookingService:
    """Service for slot management and bookings"""
    
    @staticmethod
    def create_booking(user, slot, service, notes=""):
        """
        Create a new slot booking.
        Prevents overbooking by checking availability.
        
        Args:
            user: User object (customer)
            slot: Slot object
            service: Service object
            notes: Customer notes
            
        Returns:
            SlotBooking object
        """
        # Check if slot is available
        if slot.is_fully_booked:
            raise ValueError("This slot is fully booked")
        
        # Check if slot is in the past
        slot_datetime = datetime.combine(slot.slot_date, slot.slot_start_time)
        if slot_datetime < timezone.now():
            raise ValueError("Cannot book slots in the past")
        
        # Check if user already has booking for this slot
        if SlotBooking.objects.filter(
            user=user,
            slot=slot,
            status='confirmed'
        ).exists():
            raise ValueError("You already have a booking for this slot")
        
        # Create booking
        booking_id = f"BK{uuid.uuid4().hex[:8].upper()}"
        booking = SlotBooking.objects.create(
            booking_id=booking_id,
            user=user,
            slot=slot,
            service=service,
            customer_notes=notes
        )
        
        # Increase slot bookings
        slot.current_bookings += 1
        slot.save()
        
        # Send confirmation notification
        NotificationService.send_booking_confirmation(booking)
        
        # Log audit
        AuditLog.objects.create(
            action_type='booking_created',
            description=f"Booking {booking_id} created for {user.username} on {slot}",
            user=user,
            slot_booking=booking
        )
        
        return booking
    
    @staticmethod
    def cancel_booking(booking, reason=""):
        """
        Cancel a slot booking.
        
        Args:
            booking: SlotBooking object
            reason: Cancellation reason
            
        Returns:
            SlotBooking object
        """
        if booking.status != 'confirmed':
            raise ValueError("Only confirmed bookings can be cancelled")
        
        booking.status = 'cancelled'
        booking.cancellation_reason = reason
        booking.cancelled_at = timezone.now()
        booking.save()
        
        # Decrease slot bookings
        booking.slot.current_bookings = max(0, booking.slot.current_bookings - 1)
        booking.slot.save()
        
        # Log audit
        AuditLog.objects.create(
            action_type='booking_cancelled',
            description=f"Booking {booking.booking_id} cancelled - {reason}",
            user=booking.user,
            slot_booking=booking
        )
        
        return booking
    
    @staticmethod
    def get_available_slots(service, branch, days_ahead=7):
        """
        Get available slots for a service.
        
        Args:
            service: Service object
            branch: Branch object
            days_ahead: Number of days to search ahead
            
        Returns:
            QuerySet of available Slot objects
        """
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=days_ahead)
        
        return Slot.objects.filter(
            service=service,
            counter__branch=branch,
            slot_date__range=[start_date, end_date],
            is_active=True,
            status__in=['available', 'partially_booked']
        ).order_by('slot_date', 'slot_start_time')
    
    @staticmethod
    def send_reminders():
        """
        Send reminders for upcoming bookings (24 hours before).
        Should be run as a periodic task.
        """
        tomorrow_start = timezone.now() + timedelta(days=1)
        tomorrow_end = tomorrow_start + timedelta(hours=23, minutes=59)
        
        bookings = SlotBooking.objects.filter(
            status='confirmed',
            is_reminder_sent=False,
            slot__slot_date__range=[tomorrow_start.date(), tomorrow_end.date()]
        )
        
        for booking in bookings:
            NotificationService.send_slot_reminder(booking)
            booking.is_reminder_sent = True
            booking.reminder_sent_at = timezone.now()
            booking.save()


# ============================================================================
# QUEUE SERVICE
# ============================================================================

class QueueService:
    """Service for queue management"""
    
    @staticmethod
    def get_next_token(counter):
        """
        Get the next token to serve at a counter.
        Respects priority levels.
        
        Args:
            counter: Counter object
            
        Returns:
            Token object or None
        """
        # Get waiting tokens sorted by priority and time
        token = Token.objects.filter(
            counter=counter,
            status='waiting'
        ).order_by('priority', 'generated_at').first()
        
        return token
    
    @staticmethod
    def get_queue_statistics(queue):
        """
        Get statistics for a queue.
        
        Args:
            queue: Queue object
            
        Returns:
            Dictionary with queue statistics
        """
        today = timezone.now().date()
        tokens_today = Token.objects.filter(
            queue=queue,
            generated_at__date=today
        )
        
        stats = {
            'total_tokens': tokens_today.count(),
            'waiting_tokens': tokens_today.filter(status='waiting').count(),
            'serving_tokens': tokens_today.filter(status='serving').count(),
            'completed_tokens': tokens_today.filter(status='completed').count(),
            'cancelled_tokens': tokens_today.filter(status='cancelled').count(),
            'no_show_tokens': tokens_today.filter(status='no_show').count(),
            'avg_wait_time': tokens_today.aggregate(Avg('waiting_time'))['waiting_time__avg'],
            'avg_service_time': tokens_today.aggregate(Avg('service_duration'))['service_duration__avg'],
        }
        
        return stats
    
    @staticmethod
    def get_branch_queue_status(branch):
        """
        Get queue status for all counters in a branch.
        
        Args:
            branch: Branch object
            
        Returns:
            Dictionary with counter queue information
        """
        counters = branch.get_active_counters()
        status = {}
        
        for counter in counters:
            queues = counter.queues.filter(is_active=True)
            counter_info = {
                'name': counter.name,
                'is_busy': counter.is_busy,
                'current_token': None,
                'waiting_count': 0,
                'queues': {}
            }
            
            for queue in queues:
                waiting_count = queue.get_waiting_count()
                current = queue.tokens.filter(status='serving').first()
                
                counter_info['queues'][queue.service.name] = {
                    'waiting': waiting_count,
                    'avg_wait_time': queue.current_wait_time
                }
                
                if current:
                    counter_info['current_token'] = current.token_number
                    counter_info['is_busy'] = True
            
            status[counter.counter_id] = counter_info
        
        return status


# ============================================================================
# NOTIFICATION SERVICE
# ============================================================================

class NotificationService:
    """Service for sending notifications"""
    
    @staticmethod
    def send_token_called_notification(token):
        """Send notification when token is called"""
        Notification.objects.create(
            user=token.customer,
            notification_type='token_called',
            title=f'Your Token {token.token_number} Has Been Called',
            message=f'Please proceed to Counter {token.counter.name} for service',
            token=token
        )
    
    @staticmethod
    def send_token_confirmed_notification(token):
        """Send notification when token is confirmed"""
        Notification.objects.create(
            user=token.customer,
            notification_type='token_confirmed',
            title=f'Token {token.token_number} Confirmed',
            message=f'Your token has been confirmed. Estimated wait time: {token.estimated_wait_time} minutes',
            token=token
        )
    
    @staticmethod
    def send_booking_confirmation(booking):
        """Send notification when booking is confirmed"""
        Notification.objects.create(
            user=booking.user,
            notification_type='booking_confirmation',
            title=f'Booking Confirmed - {booking.service.name}',
            message=f'Your booking for {booking.service.name} on {booking.slot.slot_date} at {booking.slot.slot_start_time} has been confirmed. Booking ID: {booking.booking_id}',
            slot_booking=booking
        )
    
    @staticmethod
    def send_slot_reminder(booking):
        """Send reminder notification for upcoming booking"""
        Notification.objects.create(
            user=booking.user,
            notification_type='slot_reminder',
            title=f'Reminder - {booking.service.name}',
            message=f'You have a booking tomorrow at {booking.slot.slot_start_time} at {booking.slot.counter.branch.name} for {booking.service.name}. Please arrive 5 minutes early.',
            slot_booking=booking
        )
    
    @staticmethod
    def send_queue_update(counter):
        """Send queue update notification to all waiting customers"""
        waiting_tokens = counter.tokens.filter(status='waiting')
        
        for token in waiting_tokens:
            Notification.objects.create(
                user=token.customer,
                notification_type='queue_update',
                title='Queue Update',
                message=f'You are #{token.queue.tokens.filter(status="waiting", priority__lte=token.priority).count()} in the queue',
                token=token
            )
    
    @staticmethod
    def send_system_alert(users, title, message):
        """Send system alert to multiple users"""
        notifications = [
            Notification(
                user=user,
                notification_type='system_alert',
                title=title,
                message=message
            )
            for user in users
        ]
        Notification.objects.bulk_create(notifications)


# ============================================================================
# ANALYTICS SERVICE
# ============================================================================

class AnalyticsService:
    """Service for analytics and reporting"""
    
    @staticmethod
    def update_queue_analytics(queue):
        """
        Update or create analytics record for a queue.
        
        Args:
            queue: Queue object
        """
        today = timezone.now().date()
        tokens = Token.objects.filter(
            queue=queue,
            generated_at__date=today
        )
        
        analytics, created = QueueAnalytics.objects.get_or_create(
            date=today,
            queue=queue
        )
        
        analytics.total_tokens = tokens.count()
        analytics.served_tokens = tokens.filter(status='completed').count()
        analytics.cancelled_tokens = tokens.filter(status='cancelled').count()
        analytics.no_show_tokens = tokens.filter(status='no_show').count()
        
        # Calculate averages
        avg_wait = tokens.aggregate(Avg('waiting_time'))['waiting_time__avg']
        analytics.avg_wait_time = int(avg_wait) if avg_wait else None
        
        avg_service = tokens.aggregate(Avg('service_duration'))['service_duration__avg']
        analytics.avg_service_time = int(avg_service) if avg_service else None
        
        # Get peak hour
        if tokens.exists():
            peak_hour = tokens.values('generated_at__hour').annotate(
                count=Count('id')
            ).order_by('-count').first()
            analytics.peak_hour = peak_hour['generated_at__hour'] if peak_hour else None
        
        # Get max queue length
        max_queue = tokens.filter(status__in=['waiting', 'called']).count()
        analytics.max_queue_length = max(analytics.max_queue_length, max_queue)
        
        analytics.save()
        
        return analytics
    
    @staticmethod
    def get_daily_report(queue, date=None):
        """
        Get daily analytics report for a queue.
        
        Args:
            queue: Queue object
            date: Date for report (default: today)
            
        Returns:
            QueueAnalytics object or None
        """
        if date is None:
            date = timezone.now().date()
        
        return QueueAnalytics.objects.filter(queue=queue, date=date).first()
    
    @staticmethod
    def get_branch_daily_report(branch, date=None):
        """
        Get daily analytics for a branch.
        
        Args:
            branch: Branch object
            date: Date for report (default: today)
            
        Returns:
            Dictionary with aggregated analytics
        """
        if date is None:
            date = timezone.now().date()
        
        queues = Queue.objects.filter(counter__branch=branch)
        analytics = QueueAnalytics.objects.filter(queue__in=queues, date=date)
        
        report = {
            'date': date,
            'branch': branch.name,
            'total_tokens': sum(a.total_tokens for a in analytics),
            'served_tokens': sum(a.served_tokens for a in analytics),
            'cancelled_tokens': sum(a.cancelled_tokens for a in analytics),
            'no_show_tokens': sum(a.no_show_tokens for a in analytics),
            'avg_wait_time': int(analytics.aggregate(Avg('avg_wait_time'))['avg_wait_time__avg'] or 0),
            'avg_service_time': int(analytics.aggregate(Avg('avg_service_time'))['avg_service_time__avg'] or 0),
            'peak_hours': [a.peak_hour for a in analytics if a.peak_hour],
        }
        
        return report
    
    @staticmethod
    def get_service_analytics(service, start_date=None, end_date=None):
        """
        Get analytics for a specific service across all queues.
        
        Args:
            service: Service object
            start_date: Start date for analysis
            end_date: End date for analysis
            
        Returns:
            Dictionary with service analytics
        """
        if start_date is None:
            start_date = timezone.now().date() - timedelta(days=30)
        if end_date is None:
            end_date = timezone.now().date()
        
        queues = Queue.objects.filter(service=service)
        analytics = QueueAnalytics.objects.filter(
            queue__in=queues,
            date__range=[start_date, end_date]
        )
        
        report = {
            'service': service.name,
            'period': f"{start_date} to {end_date}",
            'total_tokens': sum(a.total_tokens for a in analytics),
            'served_tokens': sum(a.served_tokens for a in analytics),
            'service_rate': (
                (sum(a.served_tokens for a in analytics) / sum(a.total_tokens for a in analytics) * 100)
                if sum(a.total_tokens for a in analytics) > 0 else 0
            ),
            'avg_wait_time': int(analytics.aggregate(Avg('avg_wait_time'))['avg_wait_time__avg'] or 0),
            'avg_service_time': int(analytics.aggregate(Avg('avg_service_time'))['avg_service_time__avg'] or 0),
        }
        
        return report


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_branch_status(branch):
    """Get current status of a branch"""
    return {
        'branch': branch.name,
        'is_open': branch.is_open(),
        'active_counters': branch.get_active_counters().count(),
        'total_counters': branch.counters.count(),
        'queue_status': QueueService.get_branch_queue_status(branch)
    }


def get_user_notifications(user, unread_only=False):
    """Get notifications for a user"""
    notifications = user.notifications.all()
    
    if unread_only:
        notifications = notifications.filter(is_read=False)
    
    return notifications


def mark_notification_as_read(notification):
    """Mark notification as read"""
    notification.mark_as_read()
    return notification
