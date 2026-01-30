"""
Role-based access control and permissions
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden


def role_required(required_roles):
    """Decorator to check if user has required role"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login')
            
            try:
                user_role = request.user.role.role
                if user_role not in required_roles:
                    return HttpResponseForbidden("You don't have permission to access this page.")
            except AttributeError:
                return HttpResponseForbidden("User role not found. Please contact administrator.")
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def customer_required(view_func):
    """Decorator for customer-only views"""
    return role_required(['customer'])(view_func)


def staff_required(view_func):
    """Decorator for staff-only views"""
    return role_required(['staff', 'counter_manager', 'branch_manager', 'admin'])(view_func)


def counter_manager_required(view_func):
    """Decorator for counter manager views"""
    return role_required(['counter_manager', 'branch_manager', 'admin'])(view_func)


def branch_manager_required(view_func):
    """Decorator for branch manager views"""
    return role_required(['branch_manager', 'admin'])(view_func)


def admin_required(view_func):
    """Decorator for admin-only views"""
    return role_required(['counter_manager', 'branch_manager', 'admin'])(view_func)


def staff_or_admin_required(view_func):
    """Decorator for staff or admin views"""
    return role_required(['staff', 'counter_manager', 'branch_manager', 'admin'])(view_func)
