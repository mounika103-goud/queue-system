"""
Advanced queue management services
"""
from django.utils import timezone
from django.db.models import Avg, Count, Q
from .models import Queue, Token, Counter, QueueAnalytics, Notification
from datetime import datetime, timedelta


class QueueService:
    """Service for managing queue operations"""
    
    @staticmethod
    def generate_token(queue_id, customer, priority=1, notes=""):
        """Generate a new token for a customer"""
        try:
            queue = Queue.objects.get(queue_id=queue_id)
            
            if not queue.is_active:
                return None, "Queue is currently inactive"
            
            # Calculate estimated wait time
            current_tokens = Token.objects.filter(
                queue=queue,
                status__in=['waiting', 'called']
            ).count()
            
            estimated_wait = current_tokens * queue.average_service_time
            
            # Generate token number
            token_number = f"{queue.service_type.upper()[:3]}-{Queue.objects.filter(queue_id=queue_id).count() + 1:05d}"
            
            token = Token.objects.create(
                token_number=token_number,
                queue=queue,
                customer=customer,
                priority=priority,
                estimated_wait_time=estimated_wait,
                customer_notes=notes,
                status='waiting'
            )
            
            return token, "Token generated successfully"
        
        except Queue.DoesNotExist:
            return None, "Queue not found"
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def call_next_token(queue_id, staff):
        """Call the next token in queue (respects priority)"""
        try:
            queue = Queue.objects.get(queue_id=queue_id)
            
            # Get next token respecting priority (higher priority first)
            next_token = Token.objects.filter(
                queue=queue,
                status='waiting'
            ).order_by('-priority', 'generated_at').first()
            
            if not next_token:
                return None, "No tokens waiting in queue"
            
            # Update token status
            next_token.status = 'called'
            next_token.called_at = timezone.now()
            next_token.save()
            
            # Create notification for customer
            if next_token.customer:
                Notification.objects.create(
                    user=next_token.customer,
                    notification_type='token_called',
                    title='Your Token Called',
                    message=f'Token {next_token.token_number} is being called at counter {queue.counter.counter_name}',
                    token=next_token
                )
            
            return next_token, "Token called successfully"
        
        except Queue.DoesNotExist:
            return None, "Queue not found"
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def complete_service(token_id, staff):
        """Mark service as complete for a token"""
        try:
            token = Token.objects.get(token_number=token_id)
            
            if token.status not in ['called', 'serving']:
                return False, "Invalid token status for completion"
            
            token.status = 'completed'
            token.service_ended_at = timezone.now()
            token.served_by = staff
            
            if not token.service_started_at:
                token.service_started_at = timezone.now()
            
            token.save()
            
            return True, "Service completed successfully"
        
        except Token.DoesNotExist:
            return False, "Token not found"
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def get_queue_status(queue_id):
        """Get real-time queue status"""
        try:
            queue = Queue.objects.get(queue_id=queue_id)
            
            waiting_count = Token.objects.filter(
                queue=queue,
                status='waiting'
            ).count()
            
            served_today = Token.objects.filter(
                queue=queue,
                status='completed',
                service_ended_at__date=timezone.now().date()
            ).count()
            
            avg_wait = Token.objects.filter(
                queue=queue,
                status='completed'
            ).aggregate(
                avg_wait=Avg('called_at') - Avg('generated_at')
            )
            
            return {
                'queue_id': queue.queue_id,
                'service_type': queue.get_service_type_display(),
                'waiting_count': waiting_count,
                'served_today': served_today,
                'estimated_wait': queue.current_wait_time,
                'status': queue.status
            }
        
        except Queue.DoesNotExist:
            return None
    
    @staticmethod
    def cancel_token(token_id, reason=""):
        """Cancel a token"""
        try:
            token = Token.objects.get(token_number=token_id)
            
            if token.status in ['completed', 'cancelled']:
                return False, "Cannot cancel completed or already cancelled token"
            
            token.status = 'cancelled'
            token.customer_notes = f"Cancelled. Reason: {reason}" if reason else "Cancelled"
            token.save()
            
            return True, "Token cancelled successfully"
        
        except Token.DoesNotExist:
            return False, "Token not found"
        except Exception as e:
            return False, str(e)


class AnalyticsService:
    """Service for generating analytics and reports"""
    
    @staticmethod
    def get_daily_analytics(queue_id, date=None):
        """Get daily analytics for a queue"""
        if date is None:
            date = timezone.now().date()
        
        try:
            analytics = QueueAnalytics.objects.get(
                queue__queue_id=queue_id,
                date=date
            )
            return analytics
        except QueueAnalytics.DoesNotExist:
            return None
    
    @staticmethod
    def calculate_queue_metrics(queue_id):
        """Calculate average metrics for a queue"""
        tokens = Token.objects.filter(
            queue__queue_id=queue_id,
            status='completed'
        )
        
        metrics = {
            'total_served': tokens.count(),
            'avg_wait_time': 0,
            'avg_service_time': 0,
            'peak_hour': None
        }
        
        if tokens.exists():
            # Calculate average wait time
            wait_times = []
            for token in tokens:
                if token.wait_duration:
                    wait_times.append(token.wait_duration)
            
            if wait_times:
                metrics['avg_wait_time'] = int(sum(wait_times) / len(wait_times))
            
            # Calculate average service time
            service_times = []
            for token in tokens:
                if token.service_duration:
                    service_times.append(token.service_duration)
            
            if service_times:
                metrics['avg_service_time'] = int(sum(service_times) / len(service_times))
        
        return metrics
    
    @staticmethod
    def get_overall_bank_analytics(date=None):
        """Get analytics for entire bank"""
        if date is None:
            date = timezone.now().date()
        
        analytics_data = QueueAnalytics.objects.filter(date=date)
        
        total_tokens = sum(a.total_tokens for a in analytics_data)
        total_served = sum(a.served_tokens for a in analytics_data)
        
        return {
            'date': date,
            'total_tokens': total_tokens,
            'total_served': total_served,
            'cancelled': sum(a.cancelled_tokens for a in analytics_data),
            'no_show': sum(a.no_show_tokens for a in analytics_data),
            'queues_count': analytics_data.count()
        }
