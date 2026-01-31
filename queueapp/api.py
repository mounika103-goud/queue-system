from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from queueapp.models import Token, Queue, Counter
import json
from datetime import timedelta


def staff_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        if not hasattr(request.user, 'role') or request.user.role not in ['staff', 'admin']:
            return JsonResponse({'error': 'Not authorized'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        if not hasattr(request.user, 'role') or request.user.role != 'admin':
            return JsonResponse({'error': 'Not authorized'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper


@login_required(login_url='/accounts/login/')
@require_POST
def cancel_token(request, token_id):
    """Cancel a token (customer)"""
    try:
        print(f"Cancel token request - user: {request.user}, token_id: {token_id}")
        
        token = Token.objects.get(id=token_id, customer=request.user)
        
        # Get reason from request
        try:
            data = json.loads(request.body)
            reason = data.get('reason', 'No reason provided')
        except:
            reason = request.POST.get('reason', 'No reason provided')
        
        print(f"Found token: {token}, cancelling with reason: {reason}")
        
        # Update token status
        token.status = 'cancelled'
        token.cancellation_reason = reason
        token.cancelled_at = timezone.now()
        token.save()
        
        print(f"Token {token_id} cancelled successfully")
        
        return JsonResponse({
            'status': 'success',
            'success': True,
            'message': 'Token cancelled successfully'
        })
    except Token.DoesNotExist:
        print(f"Token not found: id={token_id}, user={request.user}")
        return JsonResponse({
            'status': 'error',
            'success': False,
            'message': 'Token not found'
        }, status=404)
    except Exception as e:
        print(f"Error cancelling token: {str(e)}")
        import traceback
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@staff_required
@require_POST
def complete_token(request, token_id):
    """Mark token as completed (staff)"""
    try:
        token = Token.objects.get(id=token_id)
        
        # Update token status
        token.status = 'completed'
        token.completed_at = timezone.now()
        token.save()
        
        # Update counter availability
        counter = token.counter
        counter.is_busy = False
        counter.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Token completed successfully'
        })
    except Token.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Token not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
@staff_required
@require_POST
def skip_token(request, token_id):
    """Skip a token (staff)"""
    try:
        token = Token.objects.get(id=token_id)
        
        # Update token - move back to waiting
        token.status = 'waiting'
        token.called_at = None
        token.skip_count = (token.skip_count or 0) + 1
        token.save()
        
        # Free up counter
        counter = token.counter
        counter.is_busy = False
        counter.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Token skipped successfully'
        })
    except Token.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Token not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
@staff_required
@require_POST
def call_token(request, token_id):
    """Call a specific token (from next preview)"""
    try:
        token = Token.objects.get(id=token_id)
        counter = Counter.objects.get(staff_member=request.user)
        
        # Update token
        token.status = 'called'
        token.counter = counter
        token.called_at = timezone.now()
        token.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Token called successfully',
            'token_number': token.token_number
        })
    except Token.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Token not found'
        }, status=404)
    except Counter.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Counter not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
@staff_required
@require_POST
def call_next_from_queue(request, queue_id):
    """Call next customer from queue selection"""
    try:
        queue = Queue.objects.get(id=queue_id)
        counter = Counter.objects.get(staff_member=request.user)
        
        # Get next waiting token from this queue
        next_token = Token.objects.filter(
            queue=queue,
            status='waiting'
        ).order_by('created_at').first()
        
        if not next_token:
            return JsonResponse({
                'status': 'error',
                'message': 'No waiting tokens in this queue'
            }, status=400)
        
        # Update token
        next_token.status = 'called'
        next_token.counter = counter
        next_token.called_at = timezone.now()
        next_token.save()
        
        # Mark counter as busy
        counter.is_busy = True
        counter.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Token called successfully',
            'token_number': next_token.token_number
        })
    except Queue.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Queue not found'
        }, status=404)
    except Counter.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Counter not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
@staff_required
@require_POST
def transfer_token(request, token_id):
    """Transfer token to another counter"""
    try:
        token = Token.objects.get(id=token_id)
        
        # Get target counter from request
        data = json.loads(request.body)
        target_counter_id = data.get('counter_id')
        
        target_counter = Counter.objects.get(id=target_counter_id)
        
        # Transfer token
        token.counter = target_counter
        token.status = 'waiting'  # Move back to waiting for new counter
        token.called_at = None
        token.save()
        
        # Free up current counter
        current_counter = Counter.objects.get(staff_member=request.user)
        current_counter.is_busy = False
        current_counter.save()
        
        return JsonResponse({
            'status': 'success',
            'message': f'Token transferred to {target_counter.counter_id}'
        })
    except Token.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Token not found'
        }, status=404)
    except Counter.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Counter not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
@admin_required
@require_POST
def execute_recommendation(request, rec_id):
    """Execute a system recommendation"""
    try:
        # This is a placeholder - would implement actual recommendation logic
        rec_actions = {
            'rec_1': 'open_counter',
            'rec_2': 'view_analytics',
            'rec_3': 'view_details'
        }
        
        action = rec_actions.get(rec_id)
        
        if not action:
            return JsonResponse({
                'status': 'error',
                'message': 'Recommendation not found'
            }, status=404)
        
        return JsonResponse({
            'status': 'success',
            'message': f'Recommendation executed: {action}',
            'action': action
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


# Utility function to get token with wait calculation
def calculate_wait_time(token):
    """Calculate wait time for a token"""
    if token.called_at:
        wait_seconds = (token.called_at - token.created_at).total_seconds()
        return int(wait_seconds / 60)
    return None


# Utility function to get queue analytics
def get_queue_analytics(queue):
    """Get analytics for a specific queue"""
    today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    return {
        'waiting': Token.objects.filter(queue=queue, status='waiting').count(),
        'serving': Token.objects.filter(queue=queue, status='serving').count(),
        'completed_today': Token.objects.filter(
            queue=queue,
            status='completed',
            completed_at__gte=today_start
        ).count(),
        'avg_wait_time': Token.objects.filter(queue=queue).aggregate(
            avg=Avg('waiting_time')
        ).get('avg') or 0
    }
