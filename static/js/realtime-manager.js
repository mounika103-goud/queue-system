/**
 * Real-Time Frontend Manager
 * Handles live updates, auto-refresh, animations, and countdowns
 */

class RealtimeManager {
    constructor(options = {}) {
        this.updateInterval = options.updateInterval || 5000; // 5 seconds default
        this.autoRefresh = options.autoRefresh !== false;
        this.animationDuration = options.animationDuration || 300;
        this.activeUpdates = new Map();
        this.notifications = [];
        this.init();
    }

    init() {
        console.log('🚀 Realtime Manager initialized');
        this.setupEventListeners();
        this.startAutoRefresh();
    }

    setupEventListeners() {
        // Listen for visibility changes to pause/resume updates
        document.addEventListener('visibilitychange', () => {
            if (document.hidden) {
                this.pauseAutoRefresh();
            } else {
                this.startAutoRefresh();
            }
        });

        // Handle before unload
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
    }

    /**
     * Start auto-refresh for live updates
     */
    startAutoRefresh() {
        if (this.autoRefresh && !this.refreshTimer) {
            this.refreshTimer = setInterval(() => {
                this.refreshQueueStatus();
            }, this.updateInterval);
            console.log('✅ Auto-refresh started');
        }
    }

    /**
     * Pause auto-refresh
     */
    pauseAutoRefresh() {
        if (this.refreshTimer) {
            clearInterval(this.refreshTimer);
            this.refreshTimer = null;
            console.log('⏸️ Auto-refresh paused');
        }
    }

    /**
     * Refresh queue status with live updates
     */
    async refreshQueueStatus() {
        try {
            const response = await fetch('/api/queue-status/', {
                method: 'GET',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (response.ok) {
                const data = await response.json();
                this.updateQueueDisplay(data);
                this.checkForTokenChanges(data);
            }
        } catch (error) {
            console.warn('⚠️ Queue refresh failed:', error);
        }
    }

    /**
     * Update queue display with smooth animations
     */
    updateQueueDisplay(data) {
        const queueElements = document.querySelectorAll('[data-queue-id]');
        
        queueElements.forEach(element => {
            const queueId = element.dataset.queueId;
            const queueData = data.queues?.[queueId];

            if (queueData) {
                this.animateUpdate(element, {
                    waiting: queueData.waiting_count,
                    avgWait: queueData.avg_wait_time,
                    status: queueData.status
                });
            }
        });
    }

    /**
     * Check for token changes and trigger animations
     */
    checkForTokenChanges(data) {
        const currentTokens = data.current_tokens || {};

        Object.entries(currentTokens).forEach(([tokenId, tokenData]) => {
            const tokenElement = document.querySelector(`[data-token-id="${tokenId}"]`);
            
            if (tokenElement) {
                if (this.activeUpdates.has(tokenId)) {
                    const oldData = this.activeUpdates.get(tokenId);
                    if (oldData.status !== tokenData.status) {
                        this.triggerTokenStatusChange(tokenElement, oldData, tokenData);
                    }
                } else {
                    this.activeUpdates.set(tokenId, tokenData);
                }
            }
        });
    }

    /**
     * Trigger animation when token status changes
     */
    triggerTokenStatusChange(element, oldData, newData) {
        // Add pulse animation
        element.classList.add('pulse-animation');
        
        // Update the token status
        const statusElement = element.querySelector('[data-token-status]');
        if (statusElement) {
            statusElement.textContent = newData.status.toUpperCase();
            statusElement.className = `badge status-${newData.status}`;
        }

        // Add notification
        this.showNotification(`Token ${newData.token_number} status: ${newData.status}`, 'info');

        // Remove animation after it completes
        setTimeout(() => {
            element.classList.remove('pulse-animation');
        }, this.animationDuration);

        // Update stored data
        this.activeUpdates.set(newData.id, newData);
    }

    /**
     * Animate element update
     */
    animateUpdate(element, data) {
        element.style.opacity = '0.5';
        
        // Update content
        const waitingElement = element.querySelector('[data-waiting-count]');
        if (waitingElement) {
            waitingElement.textContent = data.waiting;
        }

        const avgWaitElement = element.querySelector('[data-avg-wait]');
        if (avgWaitElement) {
            avgWaitElement.textContent = data.avgWait;
        }

        // Fade back in
        setTimeout(() => {
            element.style.opacity = '1';
        }, this.animationDuration / 2);
    }

    /**
     * Show notification
     */
    showNotification(message, type = 'info') {
        const notification = {
            id: Date.now(),
            message,
            type,
            timestamp: new Date()
        };

        this.notifications.push(notification);

        // Create toast element
        const toast = this.createToastElement(notification);
        const container = document.querySelector('[data-notification-container]') || 
                         document.body;
        container.appendChild(toast);

        // Auto-remove after 4 seconds
        setTimeout(() => {
            toast.classList.add('fade-out');
            setTimeout(() => toast.remove(), 300);
        }, 4000);

        return notification;
    }

    /**
     * Create toast notification element
     */
    createToastElement(notification) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${notification.type} animate-slideIn`;
        toast.innerHTML = `
            <div class="toast-content">
                <span class="toast-icon">
                    ${this.getIconForType(notification.type)}
                </span>
                <span class="toast-message">${notification.message}</span>
            </div>
            <div class="toast-progress"></div>
        `;
        return toast;
    }

    /**
     * Get icon for notification type
     */
    getIconForType(type) {
        const icons = {
            'success': '✓',
            'error': '✕',
            'warning': '⚠',
            'info': 'ⓘ'
        };
        return icons[type] || 'ⓘ';
    }

    /**
     * Call token with animation
     */
    async callToken(tokenId, counterName) {
        const element = document.querySelector(`[data-token-id="${tokenId}"]`);
        
        if (element) {
            // Start calling animation
            element.classList.add('token-calling');
            
            try {
                const response = await fetch(`/api/token/${tokenId}/call/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': this.getCsrfToken(),
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ counter: counterName })
                });

                if (response.ok) {
                    this.showNotification(`Token called to ${counterName}! 📣`, 'success');
                    
                    // Trigger announcement animation
                    this.triggerAnnouncement(tokenId, counterName);
                } else {
                    this.showNotification('Failed to call token', 'error');
                    element.classList.remove('token-calling');
                }
            } catch (error) {
                console.error('Error calling token:', error);
                this.showNotification('Error calling token', 'error');
                element.classList.remove('token-calling');
            }
        }
    }

    /**
     * Trigger announcement animation
     */
    triggerAnnouncement(tokenId, counterName) {
        const announcement = document.createElement('div');
        announcement.className = 'announcement-badge animate-popIn';
        announcement.innerHTML = `
            <div class="announcement-content">
                <div class="announcement-text">
                    <strong>Counter ${counterName}</strong>
                </div>
                <div class="announcement-token">Token ${tokenId}</div>
            </div>
        `;

        const container = document.querySelector('[data-announcement-container]') || 
                         document.body;
        container.appendChild(announcement);

        // Auto-remove
        setTimeout(() => {
            announcement.classList.add('fade-out');
            setTimeout(() => announcement.remove(), 500);
        }, 3000);
    }

    /**
     * Start countdown timer
     */
    startCountdown(element, seconds, onComplete) {
        let remaining = seconds;
        
        const updateDisplay = () => {
            const mins = Math.floor(remaining / 60);
            const secs = remaining % 60;
            element.textContent = `${mins}:${secs.toString().padStart(2, '0')}`;
            
            // Add warning class when low
            if (remaining < 10) {
                element.classList.add('timer-warning');
            }
            
            remaining--;
            
            if (remaining < 0) {
                clearInterval(timer);
                if (onComplete) onComplete();
                element.classList.remove('timer-warning');
            }
        };

        updateDisplay();
        const timer = setInterval(updateDisplay, 1000);
        return timer;
    }

    /**
     * Get CSRF token from cookie
     */
    getCsrfToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value ||
               this.getCookie('csrftoken') || '';
    }

    /**
     * Get cookie value
     */
    getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    /**
     * Cleanup on page unload
     */
    cleanup() {
        this.pauseAutoRefresh();
        console.log('🧹 Realtime Manager cleaned up');
    }
}

// Initialize on document ready
document.addEventListener('DOMContentLoaded', () => {
    window.realtimeManager = new RealtimeManager({
        updateInterval: 5000,
        autoRefresh: true,
        animationDuration: 300
    });
});
