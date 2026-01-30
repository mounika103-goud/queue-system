// Real-time Updates Handler
class RealTimeUpdater {
    constructor() {
        this.updateInterval = null;
        this.isConnected = true;
        this.lastUpdate = null;
    }

    // Initialize real-time updates
    init() {
        console.log('Initializing real-time updates...');
        this.startPolling();
        this.setupConnectionMonitor();
    }

    // Start polling for updates
    startPolling() {
        // Update queue status every 5 seconds
        this.updateInterval = setInterval(() => {
            this.updateQueueStatus();
            this.updateNotifications();
        }, 5000);
    }

    // Update queue status
    updateQueueStatus() {
        const queueId = document.getElementById('queue-id');
        if (!queueId) return;

        const urlBase = '/api/queue-status/';
        const url = urlBase + queueId.value + '/';

        fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log('Queue Status:', data);
                this.updateQueueUI(data);
                this.lastUpdate = new Date();
            })
            .catch(error => {
                console.error('Error fetching queue status:', error);
            });
    }

    // Update queue UI
    updateQueueUI(data) {
        const waitingCountEl = document.getElementById('waiting-count');
        const estimatedWaitEl = document.getElementById('estimated-wait');
        const statusBadgeEl = document.getElementById('queue-status');

        if (waitingCountEl) {
            waitingCountEl.textContent = data.waiting_count || 0;
        }

        if (estimatedWaitEl) {
            estimatedWaitEl.textContent = data.estimated_wait || 0;
        }

        if (statusBadgeEl) {
            statusBadgeEl.textContent = data.status.toUpperCase();
        }
    }

    // Update notifications
    updateNotifications() {
        fetch('/api/notifications/')
            .then(response => response.json())
            .then(data => {
                if (data.count > 0) {
                    this.showNotifications(data.notifications);
                }
            })
            .catch(error => {
                console.error('Error fetching notifications:', error);
            });
    }

    // Show notifications
    showNotifications(notifications) {
        notifications.forEach(notification => {
            this.displayNotification(
                notification.title,
                notification.message,
                notification.type
            );
        });
    }

    // Display single notification
    displayNotification(title, message, type = 'info') {
        const notificationHTML = `
            <div class="alert alert-${type} alert-dismissible fade show" role="alert">
                <strong>${title}</strong>
                <p>${message}</p>
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
        `;

        const notificationContainer = document.getElementById('notifications-container');
        if (notificationContainer) {
            const tempDiv = document.createElement('div');
            tempDiv.innerHTML = notificationHTML;
            notificationContainer.appendChild(tempDiv.firstElementChild);

            // Auto-dismiss after 5 seconds
            setTimeout(() => {
                const alert = tempDiv.firstElementChild;
                if (alert) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, 5000);
        }
    }

    // Connection monitor
    setupConnectionMonitor() {
        window.addEventListener('online', () => {
            this.isConnected = true;
            console.log('Connection restored');
            this.displayNotification('Connection', 'Connected to server', 'success');
        });

        window.addEventListener('offline', () => {
            this.isConnected = false;
            console.log('Connection lost');
            this.displayNotification('Connection', 'Connection lost. Updates paused.', 'danger');
        });
    }

    // Stop updates
    stop() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Token Status Updater
class TokenStatusUpdater {
    constructor(tokenId) {
        this.tokenId = tokenId;
        this.updateInterval = null;
        this.isComplete = false;
    }

    init() {
        console.log(`Initializing token status updates for ${this.tokenId}`);
        this.startPolling();
    }

    startPolling() {
        // Update token status every 3 seconds
        this.updateInterval = setInterval(() => {
            if (!this.isComplete) {
                this.updateTokenStatus();
            }
        }, 3000);
    }

    updateTokenStatus() {
        const url = `/api/token-status/${this.tokenId}/`;

        fetch(url)
            .then(response => response.json())
            .then(data => {
                console.log('Token Status:', data);
                this.updateTokenUI(data);

                // Check if service is complete
                if (data.status === 'completed') {
                    this.isComplete = true;
                    this.showCompletionNotification();
                    clearInterval(this.updateInterval);
                }
            })
            .catch(error => {
                console.error('Error fetching token status:', error);
            });
    }

    updateTokenUI(data) {
        const statusEl = document.getElementById('token-status');
        const counterEl = document.getElementById('token-counter');
        const waitTimeEl = document.getElementById('token-wait-time');

        if (statusEl) {
            statusEl.textContent = data.status.toUpperCase();
            statusEl.className = `badge bg-${this.getStatusColor(data.status)}`;
        }

        if (counterEl) {
            counterEl.textContent = data.counter;
        }

        if (waitTimeEl && data.estimated_wait) {
            waitTimeEl.textContent = `${data.estimated_wait} minutes`;
        }
    }

    getStatusColor(status) {
        const colors = {
            'waiting': 'warning',
            'called': 'success',
            'serving': 'info',
            'completed': 'success',
            'cancelled': 'danger',
            'no_show': 'danger'
        };
        return colors[status] || 'secondary';
    }

    showCompletionNotification() {
        const sound = new Audio('/static/sounds/success.mp3');
        sound.play().catch(e => console.log('Audio play failed:', e));

        alert(`Token ${this.tokenId} - Service Completed! Thank you for using our service.`);
    }

    stop() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    console.log('DOM ready - initializing real-time updates');

    // Initialize real-time updater if on main page
    const queueId = document.getElementById('queue-id');
    if (queueId) {
        const updater = new RealTimeUpdater();
        updater.init();
    }

    // Initialize token status updater if on token status page
    const tokenId = document.getElementById('token-id');
    if (tokenId) {
        const tokenUpdater = new TokenStatusUpdater(tokenId.value);
        tokenUpdater.init();
    }
});
