from django.urls import path
from . import views
from .api import (
    cancel_token, complete_token, skip_token, call_token,
    call_next_from_queue, transfer_token, execute_recommendation
)

app_name = 'queueapp'

urlpatterns = [
    # Home and dashboard
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('demo/realtime/', views.realtime_demo, name='realtime_demo'),
    
    # Customer URLs
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('customer/get-token/', views.get_token, name='get_token'),
    path('customer/generate-token-ajax/', views.generate_token_ajax, name='generate_token_ajax'),
    path('customer/token/<str:token_id>/', views.token_status, name='token_status'),
    path('customer/history/', views.customer_history, name='customer_history'),
    
    # Staff URLs
    path('dashboard/staff/', views.staff_dashboard, name='staff_dashboard'),
    path('staff/serve-queue/', views.serve_queue, name='serve_queue'),
    path('staff/call-next/', views.call_next_token, name='call_next_token'),
    path('staff/complete-service/', views.complete_service, name='complete_service'),
    
    # Admin URLs
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/analytics/', views.analytics, name='analytics'),
    path('admin/manage-counters/', views.manage_counters, name='manage_counters'),
    path('admin/manage-queues/', views.manage_queues, name='manage_queues'),
    
    # API endpoints - Token operations
    path('api/token/<int:token_id>/cancel/', cancel_token, name='api_cancel_token'),
    path('api/token/<int:token_id>/complete/', complete_token, name='api_complete_token'),
    path('api/token/<int:token_id>/skip/', skip_token, name='api_skip_token'),
    path('api/token/<int:token_id>/call/', call_token, name='api_call_token'),
    path('api/token/<int:token_id>/transfer/', transfer_token, name='api_transfer_token'),
    
    # API endpoints - Queue operations
    path('api/queue/<int:queue_id>/call-next/', call_next_from_queue, name='api_call_next'),
    
    # API endpoints - Recommendations
    path('api/recommendation/<str:rec_id>/execute/', execute_recommendation, name='api_execute_rec'),
    
    # Existing API endpoints
    path('api/queue-status/<str:queue_id>/', views.api_queue_status, name='api_queue_status'),
    path('api/token-status/<str:token_id>/', views.api_token_status, name='api_token_status'),
    path('api/notifications/', views.api_notifications, name='api_notifications'),
]
