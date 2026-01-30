/**
 * Notifications Manager
 * Handles fetching, displaying, and managing user notifications
 */

class NotificationsManager {
    constructor() {
        this.dropdownList = document.getElementById('notificationList');
        this.badge = document.getElementById('notificationBadge');
        this.updateInterval = 30000; // 30 seconds
        this.apiEndpoint = '/api/notifications/';
        this.maxNotifications = 10;
        
        this.init();
    }

    init() {
        // Fetch notifications on load
        this.fetchNotifications();
        
        // Set up auto-refresh
        setInterval(() => this.fetchNotifications(), this.updateInterval);
    }

    /**
     * Fetch notifications from API
     */
    async fetchNotifications() {
        try {
            const response = await fetch(this.apiEndpoint);
            if (!response.ok) throw new Error('Failed to fetch notifications');
            
            const data = await response.json();
            this.renderNotifications(data.notifications || []);
            this.updateBadge(data.unread_count || 0);
        } catch (error) {
            console.error('Notification fetch error:', error);
        }
    }

    /**
     * Render notifications in dropdown
     */
    renderNotifications(notifications) {
        if (!this.dropdownList) return;

        if (notifications.length === 0) {
            this.dropdownList.innerHTML = `
                <li class="text-center p-3 text-muted">
                    <small><i class="fas fa-bell-slash me-2"></i>No notifications</small>
                </li>
            `;
            return;
        }

        // Limit displayed notifications
        const displayNotifications = notifications.slice(0, this.maxNotifications);
        
        const html = displayNotifications.map(notif => {
            const icon = this.getNotificationIcon(notif.type);
            const timeAgo = this.getTimeAgo(notif.created_at);
            const unreadClass = notif.is_read ? '' : 'bg-light';
            
            return `
                <li class="notification-item ${unreadClass} border-bottom">
                    <a href="${notif.link || '#'}" class="dropdown-item p-3 d-flex gap-2 text-decoration-none"
                       onclick="notificationsManager.markAsRead(${notif.id})">
                        <i class="fas ${icon} text-primary flex-shrink-0 mt-1"></i>
                        <div class="flex-grow-1">
                            <div class="text-body">
                                <small class="fw-500">${notif.title}</small>
                            </div>
                            <div class="text-muted">
                                <small>${notif.message}</small>
                            </div>
                            <div class="text-secondary">
                                <small>${timeAgo}</small>
                            </div>
                        </div>
                    </a>
                </li>
            `;
        }).join('');

        // Add view all link if there are more notifications
        const viewAllHtml = notifications.length > this.maxNotifications ? `
            <li class="dropdown-divider"></li>
            <li class="text-center">
                <a href="/notifications/" class="dropdown-item py-2 text-primary">
                    <small>View all notifications</small>
                </a>
            </li>
        ` : '';

        this.dropdownList.innerHTML = html + viewAllHtml;
    }

    /**
     * Get icon based on notification type
     */
    getNotificationIcon(type) {
        const icons = {
            'token_called': 'fa-bell',
            'token_completed': 'fa-check-circle',
            'token_cancelled': 'fa-times-circle',
            'counter_assigned': 'fa-door-open',
            'queue_empty': 'fa-inbox',
            'system_alert': 'fa-exclamation-triangle',
            'message': 'fa-envelope',
            'default': 'fa-bell'
        };
        return icons[type] || icons['default'];
    }

    /**
     * Calculate time ago string
     */
    getTimeAgo(timestamp) {
        const now = new Date();
        const date = new Date(timestamp);
        const seconds = Math.floor((now - date) / 1000);

        if (seconds < 60) return 'Just now';
        const minutes = Math.floor(seconds / 60);
        if (minutes < 60) return `${minutes}m ago`;
        const hours = Math.floor(minutes / 60);
        if (hours < 24) return `${hours}h ago`;
        const days = Math.floor(hours / 24);
        if (days < 7) return `${days}d ago`;
        
        return date.toLocaleDateString();
    }

    /**
     * Update notification badge
     */
    updateBadge(count) {
        if (!this.badge) return;

        if (count > 0) {
            this.badge.textContent = count > 99 ? '99+' : count;
            this.badge.style.display = 'inline-block';
        } else {
            this.badge.style.display = 'none';
        }
    }

    /**
     * Mark notification as read
     */
    async markAsRead(notificationId) {
        try {
            const response = await fetch(`/api/notifications/${notificationId}/read/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.getCsrfToken(),
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                // Refresh notifications
                this.fetchNotifications();
            }
        } catch (error) {
            console.error('Error marking notification as read:', error);
        }
    }

    /**
     * Get CSRF token from cookies
     */
    getCsrfToken() {
        const name = 'csrftoken';
        let cookieValue = null;
        
        if (document.cookie && document.cookie !== '') {
            document.cookie.split(';').forEach(cookie => {
                cookie = cookie.trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                }
            });
        }
        
        return cookieValue;
    }

    /**
     * Show toast notification
     */
    showToast(title, message, type = 'info', duration = 5000) {
        const toastHtml = `
            <div class="toast align-items-center text-white bg-${type === 'success' ? 'success' : type === 'error' ? 'danger' : 'info'} border-0" 
                 role="alert" aria-live="assertive" aria-atomic="true">
                <div class="d-flex">
                    <div class="toast-body">
                        <strong>${title}</strong><br>
                        ${message}
                    </div>
                    <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
                </div>
            </div>
        `;

        // Create toast container if it doesn't exist
        let toastContainer = document.getElementById('toastContainer');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.id = 'toastContainer';
            toastContainer.style.position = 'fixed';
            toastContainer.style.top = '20px';
            toastContainer.style.right = '20px';
            toastContainer.style.zIndex = '9999';
            document.body.appendChild(toastContainer);
        }

        // Add toast to container
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = toastHtml;
        const toastElement = tempDiv.firstElementChild;
        toastContainer.appendChild(toastElement);

        // Initialize and show Bootstrap toast
        const toast = new bootstrap.Toast(toastElement);
        toast.show();

        // Remove from DOM after it's hidden
        toastElement.addEventListener('hidden.bs.toast', () => {
            toastElement.remove();
        });

        // Auto-hide after duration
        if (duration > 0) {
            setTimeout(() => {
                toast.hide();
            }, duration);
        }
    }
}

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    window.notificationsManager = new NotificationsManager();
});

// Fallback initialization
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.notificationsManager) {
            window.notificationsManager = new NotificationsManager();
        }
    });
} else {
    if (!window.notificationsManager) {
        window.notificationsManager = new NotificationsManager();
    }
}

/**
 * Real-time notification listener (for future WebSocket integration)
 */
function subscribeToNotifications() {
    // This function can be expanded to use WebSocket instead of polling
    // when Django Channels is integrated
    
    // Example implementation:
    /*
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const socket = new WebSocket(
        `${protocol}//${window.location.host}/ws/notifications/`
    );

    socket.onmessage = function(event) {
        const data = JSON.parse(event.data);
        window.notificationsManager.showToast(
            data.title,
            data.message,
            data.type
        );
        window.notificationsManager.fetchNotifications();
    };
    */
}
