"""
Utility functions for queue management
"""
import random
import string
from datetime import datetime, timedelta


def generate_token_number(prefix, sequence):
    """Generate a unique token number"""
    return f"{prefix}-{sequence:05d}"


def format_wait_time(minutes):
    """Format wait time in human readable format"""
    if minutes < 1:
        return "Less than 1 minute"
    elif minutes == 1:
        return "1 minute"
    else:
        return f"{minutes} minutes"


def get_priority_label(priority_level):
    """Get human readable priority label"""
    priority_map = {
        1: "Normal",
        2: "Senior Citizen / PWD",
        3: "VIP",
        4: "Emergency"
    }
    return priority_map.get(priority_level, "Normal")


def get_token_status_color(status):
    """Get color code for token status"""
    status_colors = {
        'generated': '#FFC107',
        'waiting': '#17A2B8',
        'called': '#28A745',
        'serving': '#007BFF',
        'completed': '#6C757D',
        'cancelled': '#DC3545',
        'no_show': '#E83E8C'
    }
    return status_colors.get(status, '#6C757D')


def estimate_wait_time(queue_tokens_count, avg_service_time):
    """Estimate wait time based on queue length and average service time"""
    return queue_tokens_count * avg_service_time


def get_peak_hour():
    """Determine peak hour based on current time"""
    current_hour = datetime.now().hour
    
    # Define peak hours (typically 10-12 and 2-4 PM for banks)
    if 10 <= current_hour < 12:
        return "Late Morning Peak"
    elif 14 <= current_hour < 16:
        return "Afternoon Peak"
    else:
        return "Normal Hours"


def generate_analytics_report(tokens):
    """Generate analytics report from tokens"""
    if not tokens.exists():
        return {
            'total': 0,
            'served': 0,
            'cancelled': 0,
            'no_show': 0,
            'avg_wait_time': 0,
            'avg_service_time': 0
        }
    
    served_count = 0
    cancelled_count = 0
    no_show_count = 0
    wait_times = []
    service_times = []
    
    for token in tokens:
        if token.status == 'completed':
            served_count += 1
            if token.wait_duration:
                wait_times.append(token.wait_duration)
            if token.service_duration:
                service_times.append(token.service_duration)
        elif token.status == 'cancelled':
            cancelled_count += 1
        elif token.status == 'no_show':
            no_show_count += 1
    
    return {
        'total': tokens.count(),
        'served': served_count,
        'cancelled': cancelled_count,
        'no_show': no_show_count,
        'avg_wait_time': int(sum(wait_times) / len(wait_times)) if wait_times else 0,
        'avg_service_time': int(sum(service_times) / len(service_times)) if service_times else 0
    }


def get_busy_counters(counters):
    """Identify busy counters"""
    busy_counters = []
    for counter in counters:
        active_queues = counter.queues.filter(is_active=True)
        total_tokens = sum(q.tokens.filter(status__in=['waiting', 'called']).count() for q in active_queues)
        
        if total_tokens > 5:  # Threshold for busy
            busy_counters.append({
                'counter': counter,
                'token_count': total_tokens,
                'status': 'Busy'
            })
    
    return busy_counters
