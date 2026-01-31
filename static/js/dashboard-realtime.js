// Real-time Dashboard Updates
// Auto-refresh dashboard data every 5 seconds

(function() {
    'use strict';

    // Update timer for service/wait times
    function updateTimers() {
        const timeElements = document.querySelectorAll('[data-time]');
        timeElements.forEach(el => {
            const timestamp = el.getAttribute('data-time');
            if (timestamp) {
                const date = new Date(timestamp);
                const now = new Date();
                const seconds = Math.floor((now - date) / 1000);
                
                if (seconds < 60) {
                    el.textContent = seconds + 's ago';
                } else if (seconds < 3600) {
                    const minutes = Math.floor(seconds / 60);
                    el.textContent = minutes + 'm ago';
                } else {
                    const hours = Math.floor(seconds / 3600);
                    el.textContent = hours + 'h ago';
                }
            }
        });

        // Update service timer
        const serviceTimer = document.getElementById('serviceTimer');
        if (serviceTimer && serviceTimer.dataset.startTime) {
            const startTime = new Date(serviceTimer.dataset.startTime);
            const elapsed = Math.floor((new Date() - startTime) / 1000);
            const minutes = Math.floor(elapsed / 60);
            const secs = elapsed % 60;
            serviceTimer.textContent = minutes + 'm ' + secs + 's';
        }

        // Update waiting timer
        const waitingTimer = document.getElementById('waitingTimer');
        if (waitingTimer && waitingTimer.dataset.startTime) {
            const startTime = new Date(waitingTimer.dataset.startTime);
            const elapsed = Math.floor((new Date() - startTime) / 1000);
            waitingTimer.textContent = elapsed + 's';
        }
    }

    // Auto-refresh dashboard data
    function refreshDashboardData() {
        const dashboardType = document.body.getAttribute('data-dashboard-type');
        
        if (dashboardType === 'staff') {
            refreshStaffDashboard();
        } else if (dashboardType === 'customer') {
            refreshCustomerDashboard();
        } else if (dashboardType === 'admin') {
            refreshAdminDashboard();
        }
    }

    // Refresh staff dashboard
    function refreshStaffDashboard() {
        const counterId = document.body.getAttribute('data-counter-id');
        if (!counterId) return;

        fetch(`/api/counter/${counterId}/status/`)
            .then(response => response.json())
            .then(data => {
                if (data.waiting_count !== undefined) {
                    updateElement('waiting-count', data.waiting_count);
                }
                if (data.currently_serving !== undefined) {
                    updateElement('currently-serving', data.currently_serving);
                }
                if (data.efficiency !== undefined) {
                    updateElement('efficiency-percent', data.efficiency + '%');
                    updateEfficiencyCircle(data.efficiency);
                }
                if (data.counter_load !== undefined) {
                    updateElement('counter-load', data.counter_load);
                    updateLoadBar(data.counter_load);
                }
                if (data.tokens_today !== undefined) {
                    updateElement('tokens-today', data.tokens_today);
                }
            })
            .catch(err => console.log('Staff dashboard update failed:', err));
    }

    // Refresh customer dashboard
    function refreshCustomerDashboard() {
        const customerId = document.body.getAttribute('data-customer-id');
        if (!customerId) return;

        fetch(`/api/customer/${customerId}/status/`)
            .then(response => response.json())
            .then(data => {
                if (data.people_ahead !== undefined) {
                    updateElement('people-ahead', data.people_ahead);
                }
                if (data.expected_wait !== undefined) {
                    updateElement('expected-wait', data.expected_wait + ' min');
                }
                if (data.current_status !== undefined) {
                    updateElement('token-status', data.current_status);
                }
                if (data.queue_position !== undefined) {
                    const position = data.queue_position;
                    const total = data.queue_total || 100;
                    const percentage = (position / total) * 100;
                    updateElement('queue-progress', Math.min(percentage, 100) + '%');
                }
            })
            .catch(err => console.log('Customer dashboard update failed:', err));
    }

    // Refresh admin dashboard
    function refreshAdminDashboard() {
        fetch('/api/admin/dashboard-metrics/')
            .then(response => response.json())
            .then(data => {
                if (data.waiting_tokens !== undefined) {
                    updateElement('total-waiting', data.waiting_tokens);
                }
                if (data.being_served !== undefined) {
                    updateElement('being-served', data.being_served);
                }
                if (data.system_efficiency !== undefined) {
                    updateElement('system-efficiency', data.system_efficiency + '%');
                }
                if (data.avg_wait_time !== undefined) {
                    updateElement('avg-wait-time', data.avg_wait_time + ' min');
                }
                if (data.avg_service_time !== undefined) {
                    updateElement('avg-service-time', data.avg_service_time + ' min');
                }
                if (data.tokens_per_hour !== undefined) {
                    updateElement('tokens-per-hour', data.tokens_per_hour);
                }
            })
            .catch(err => console.log('Admin dashboard update failed:', err));
    }

    // Helper function to update element content
    function updateElement(elementId, value) {
        const el = document.getElementById(elementId);
        if (el) {
            const currentValue = el.textContent.trim();
            if (currentValue !== String(value)) {
                el.textContent = value;
                el.classList.add('flash-update');
                setTimeout(() => el.classList.remove('flash-update'), 500);
            }
        }
    }

    // Update efficiency circle animation
    function updateEfficiencyCircle(percentage) {
        const circle = document.querySelector('.efficiency-progress');
        if (circle) {
            const circumference = 2 * Math.PI * 90;
            const offset = circumference - (percentage / 100) * circumference;
            circle.style.strokeDasharray = `${offset} ${circumference}`;
        }
    }

    // Update load bar
    function updateLoadBar(loadPercentage) {
        const loadBar = document.querySelector('.counter-load-bar .progress-bar');
        if (loadBar) {
            loadBar.style.width = loadPercentage + '%';
        }
    }

    // Initialize updates
    function init() {
        // Update timers immediately and then every second
        updateTimers();
        setInterval(updateTimers, 1000);

        // Refresh dashboard data every 5 seconds
        refreshDashboardData();
        setInterval(refreshDashboardData, 5000);

        // Update last update timestamp
        updateLastUpdate();
        setInterval(updateLastUpdate, 60000);
    }

    // Update "last updated" timestamp
    function updateLastUpdate() {
        const lastUpdateEl = document.getElementById('lastUpdate');
        if (lastUpdateEl) {
            const now = new Date();
            lastUpdateEl.textContent = now.toLocaleTimeString();
        }
    }

    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose refresh function to global scope for manual refresh
    window.refreshDashboard = refreshDashboardData;
})();

// Add CSS animation for flash updates
const style = document.createElement('style');
style.textContent = `
    @keyframes flashUpdate {
        0% { background-color: #fff3cd; }
        100% { background-color: transparent; }
    }
    
    .flash-update {
        animation: flashUpdate 0.5s ease-out;
    }
`;
document.head.appendChild(style);
