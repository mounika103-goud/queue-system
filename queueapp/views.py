from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import Avg, Count, Q
from django.utils import timezone
from django.urls import reverse
from django.db import transaction

from .models import Queue, Token, Counter, UserRole, Notification, QueueAnalytics
from .services import QueueService, AnalyticsService
from .permissions import customer_required, staff_required, admin_required, counter_manager_required
from .utils import format_wait_time, get_priority_label, generate_analytics_report


# Home and Basic Views
def home(request):
    """Home page"""
    context = {
        'page_title': 'Smart Banking Queue Management',
    }
    return render(request, 'home.html', context)


def register(request):
    """User registration view"""
    if request.user.is_authenticated:
        return redirect('queueapp:dashboard')
    
    if request.method == 'POST':
        # Get form data
        full_name = request.POST.get('full_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        password_confirm = request.POST.get('password_confirm', '')
        account_type = request.POST.get('account_type', 'customer')
        
        # Validation
        errors = {}
        
        if not full_name:
            errors['full_name'] = 'Full name is required.'
        if not email or '@' not in email:
            errors['email'] = 'Valid email address is required.'
        if not phone:
            errors['phone'] = 'Phone number is required.'
        if not username or len(username) < 3:
            errors['username'] = 'Username must be at least 3 characters.'
        if not password or len(password) < 6:
            errors['password'] = 'Password must be at least 6 characters.'
        if password != password_confirm:
            errors['password_confirm'] = 'Passwords do not match.'
        
        # Check if username exists
        if User.objects.filter(username=username).exists():
            errors['username'] = 'Username already exists.'
        
        # Check if email exists
        if User.objects.filter(email=email).exists():
            errors['email'] = 'Email already registered.'
        
        if errors:
            context = {
                'page_title': 'Secure Registration',
                'form_data': request.POST,
                'errors': errors,
            }
            return render(request, 'register.html', context)
        
        # Create user with transaction
        try:
            with transaction.atomic():
                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=full_name.split()[0],
                    last_name=' '.join(full_name.split()[1:]) if len(full_name.split()) > 1 else ''
                )
                
                # Assign role
                role = 'customer' if account_type == 'customer' else 'staff'
                UserRole.objects.create(user=user, role=role, is_active=True)
                
                messages.success(
                    request,
                    f'✅ Registration successful! Your account "{username}" is ready. Please log in to continue.'
                )
                
                # Redirect to login
                return redirect('login')
        
        except Exception as e:
            messages.error(request, f'Registration failed: {str(e)}')
            context = {
                'page_title': 'Secure Registration',
                'form_data': request.POST,
            }
            return render(request, 'register.html', context)
    
    context = {
        'page_title': 'Secure Registration',
    }
    return render(request, 'register.html', context)


def realtime_demo(request):
    """Real-time features demo page"""
    return render(request, 'demo/realtime-demo.html', {
        'page_title': 'Real-Time Features Demo'
    })


@login_required
def dashboard(request):
    """Main dashboard - routes to appropriate dashboard based on role"""
    try:
        user_role = request.user.role.role
        
        if user_role == 'customer':
            return redirect('queueapp:customer_dashboard')
        elif user_role in ['staff', 'counter_manager', 'branch_manager']:
            return redirect('queueapp:staff_dashboard')
        elif user_role == 'admin':
            return redirect('queueapp:admin_dashboard')
        else:
            messages.error(request, 'Unknown role assigned.')
            return redirect('queueapp:home')
    except AttributeError:
        messages.error(request, 'User role not configured. Please contact administrator.')
        return redirect('queueapp:home')


# Customer Views
@login_required
@customer_required
def customer_dashboard(request):
    """Customer dashboard"""
    user_tokens = Token.objects.filter(customer=request.user)
    customer_tokens = user_tokens.order_by('-generated_at')[:5]
    active_queues = Queue.objects.filter(is_active=True)
    current_token = user_tokens.filter(status__in=['generated', 'waiting', 'called', 'being_served']).first()
    
    completed_count = user_tokens.filter(status='completed').count()
    
    context = {
        'page_title': 'Customer Dashboard',
        'recent_tokens': customer_tokens,
        'active_queues': active_queues,
        'total_tokens': user_tokens.count(),
        'current_token': current_token,
        'completed_tokens': completed_count,
        'avg_wait_time': 15,
        'time_saved': 45,
    }
    return render(request, 'customer/dashboard.html', context)


@login_required
@customer_required
def get_token(request):
    """Generate a new token"""
    if request.method == 'POST':
        queue_id = request.POST.get('queue_id')
        priority = int(request.POST.get('priority', 1))
        notes = request.POST.get('notes', '')
        
        token, message = QueueService.generate_token(queue_id, request.user, priority, notes)
        
        if token:
            messages.success(request, f'Token generated: {token.token_number}')
            return redirect('queueapp:token_status', token_id=token.token_number)
        else:
            messages.error(request, message)
    
    active_queues = Queue.objects.filter(is_active=True)
    context = {
        'page_title': 'Get Token',
        'active_queues': active_queues,
    }
    return render(request, 'customer/get_token.html', context)


@login_required
@customer_required
def token_status(request, token_id):
    """View token status"""
    token = get_object_or_404(Token, token_number=token_id)
    
    if token.customer != request.user and not request.user.is_staff:
        messages.error(request, 'You can only view your own tokens.')
        return redirect('queueapp:customer_dashboard')
    
    context = {
        'page_title': f'Token {token.token_number}',
        'token': token,
        'wait_time': format_wait_time(token.estimated_wait_time) if token.estimated_wait_time else 'Calculating...',
        'priority_label': get_priority_label(token.priority),
    }
    return render(request, 'customer/token_status.html', context)


@login_required
@customer_required
def customer_history(request):
    """View customer's token history"""
    tokens = Token.objects.filter(customer=request.user).order_by('-generated_at')
    
    # Pagination
    page = request.GET.get('page', 1)
    per_page = 20
    
    context = {
        'page_title': 'My History',
        'tokens': tokens[:per_page],
        'total_tokens': tokens.count(),
    }
    return render(request, 'customer/history.html', context)


# Staff Views
@login_required
@staff_required
def staff_dashboard(request):
    """Staff dashboard"""
    try:
        counter = Counter.objects.get(staff_member=request.user)
        queues = counter.queues.filter(is_active=True)
        
        current_tokens = Token.objects.filter(
            queue__in=queues,
            status__in=['waiting', 'called']
        ).order_by('-priority', 'generated_at')
        
        context = {
            'page_title': 'Staff Dashboard',
            'counter': counter,
            'queues': queues,
            'current_tokens': current_tokens,
            'tokens_count': current_tokens.count(),
        }
    except Counter.DoesNotExist:
        context = {
            'page_title': 'Staff Dashboard',
            'error': 'Counter not assigned to you.',
        }
    
    return render(request, 'staff/dashboard.html', context)


@login_required
@staff_required
def serve_queue(request):
    """Serve queue - manage current serving token"""
    try:
        counter = Counter.objects.get(staff_member=request.user)
        
        # Get currently serving token
        serving_token = Token.objects.filter(
            queue__counter=counter,
            status='serving'
        ).first()
        
        # Get next waiting token
        queues = counter.queues.filter(is_active=True)
        waiting_tokens = Token.objects.filter(
            queue__in=queues,
            status='called'
        ).order_by('-priority', 'called_at')
        
        context = {
            'page_title': 'Serve Queue',
            'counter': counter,
            'serving_token': serving_token,
            'waiting_tokens': waiting_tokens,
        }
    except Counter.DoesNotExist:
        context = {'error': 'Counter not assigned.'}
    
    return render(request, 'staff/serve_queue.html', context)


@login_required
@staff_required
@require_http_methods(["POST"])
def call_next_token(request):
    """Call next token in queue"""
    counter_id = request.POST.get('counter_id')
    queue_id = request.POST.get('queue_id')
    
    try:
        counter = Counter.objects.get(id=counter_id, staff_member=request.user)
        token, message = QueueService.call_next_token(queue_id, request.user)
        
        if token:
            messages.success(request, f'Calling token {token.token_number}')
            return redirect('queueapp:serve_queue')
        else:
            messages.info(request, message)
    except Counter.DoesNotExist:
        messages.error(request, 'Counter not assigned.')
    
    return redirect('queueapp:serve_queue')


@login_required
@staff_required
@require_http_methods(["POST"])
def complete_service(request):
    """Mark service as complete"""
    token_id = request.POST.get('token_id')
    
    success, message = QueueService.complete_service(token_id, request.user)
    
    if success:
        messages.success(request, message)
    else:
        messages.error(request, message)
    
    return redirect('queueapp:serve_queue')


# Admin Views
@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard with overview"""
    counters = Counter.objects.all()
    queues = Queue.objects.all()
    all_tokens = Token.objects.all()
    
    total_tokens_today = Token.objects.filter(
        generated_at__date=timezone.now().date()
    ).count()
    
    served_today = Token.objects.filter(
        generated_at__date=timezone.now().date(),
        status='completed'
    ).count()
    
    active_customers = Token.objects.filter(
        status__in=['waiting', 'called', 'called']
    ).values('customer').distinct().count()
    
    context = {
        'page_title': 'Admin Dashboard',
        'total_counters': counters.count(),
        'total_queues': queues.count(),
        'total_tokens': all_tokens.count(),
        'total_tokens_today': total_tokens_today or all_tokens.count(),
        'served_today': served_today,
        'active_customers': active_customers,
        'waiting_tokens': all_tokens.filter(status='waiting').count(),
        'being_served': all_tokens.filter(status='being_served').count(),
        'counters': counters,
        'queues': queues,
        'recent_tokens': all_tokens.order_by('-generated_at')[:10],
    }
    return render(request, 'admin/dashboard.html', context)


@login_required
@admin_required
def analytics(request):
    """Analytics and reports"""
    date = request.GET.get('date')
    
    analytics_data = QueueAnalytics.objects.all()
    
    if date:
        analytics_data = analytics_data.filter(date=date)
    
    queues = Queue.objects.all()
    queue_metrics = {}
    
    for queue in queues:
        queue_metrics[queue.queue_id] = AnalyticsService.calculate_queue_metrics(queue.queue_id)
    
    overall = AnalyticsService.get_overall_bank_analytics()
    
    context = {
        'page_title': 'Analytics & Reports',
        'analytics': analytics_data,
        'overall': overall,
        'queue_metrics': queue_metrics,
    }
    return render(request, 'admin/analytics.html', context)


@login_required
@admin_required
def manage_counters(request):
    """Manage counters"""
    counters = Counter.objects.all()
    
    context = {
        'page_title': 'Manage Counters',
        'counters': counters,
    }
    return render(request, 'admin/manage_counters.html', context)


@login_required
@admin_required
def manage_queues(request):
    """Manage queues"""
    queues = Queue.objects.all()
    
    context = {
        'page_title': 'Manage Queues',
        'queues': queues,
    }
    return render(request, 'admin/manage_queues.html', context)


# API Endpoints for Real-time Updates
@login_required
@require_http_methods(["GET"])
def api_queue_status(request, queue_id):
    """API endpoint for queue status"""
    status = QueueService.get_queue_status(queue_id)
    
    if status:
        return JsonResponse(status)
    return JsonResponse({'error': 'Queue not found'}, status=404)


@login_required
@require_http_methods(["GET"])
def api_token_status(request, token_id):
    """API endpoint for token status"""
    try:
        token = Token.objects.get(token_number=token_id)
        
        return JsonResponse({
            'token_number': token.token_number,
            'status': token.status,
            'priority': token.priority,
            'estimated_wait': token.estimated_wait_time,
            'counter': token.queue.counter.counter_name,
            'queue': token.queue.get_service_type_display(),
        })
    except Token.DoesNotExist:
        return JsonResponse({'error': 'Token not found'}, status=404)


@login_required
@require_http_methods(["GET"])
def api_notifications(request):
    """API endpoint for user notifications"""
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    
    return JsonResponse({
        'count': notifications.count(),
        'notifications': [
            {
                'id': n.id,
                'title': n.title,
                'message': n.message,
                'type': n.notification_type,
                'created_at': n.created_at.isoformat(),
            }
            for n in notifications[:10]
        ]
    })