// Chart Initialization for Analytics
class AnalyticsCharts {
    constructor() {
        this.charts = {};
    }

    // Initialize all charts
    initCharts() {
        console.log('Initializing analytics charts...');
        this.initDailyTrendChart();
        this.initServiceDistributionChart();
        this.initCounterPerformanceChart();
    }

    // Daily Trend Chart
    initDailyTrendChart() {
        const canvas = document.getElementById('dailyChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        this.charts.daily = new Chart(ctx, {
            type: 'line',
            data: {
                labels: ['8 AM', '9 AM', '10 AM', '11 AM', '12 PM', '1 PM', '2 PM', '3 PM', '4 PM'],
                datasets: [
                    {
                        label: 'Tokens Generated',
                        data: [12, 19, 25, 35, 42, 38, 28, 22, 15],
                        borderColor: '#0d6efd',
                        backgroundColor: 'rgba(13, 110, 253, 0.1)',
                        tension: 0.4,
                        borderWidth: 2,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: '#0d6efd',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    },
                    {
                        label: 'Tokens Served',
                        data: [10, 17, 22, 32, 40, 35, 26, 20, 14],
                        borderColor: '#198754',
                        backgroundColor: 'rgba(25, 135, 84, 0.1)',
                        tension: 0.4,
                        borderWidth: 2,
                        fill: true,
                        pointRadius: 4,
                        pointBackgroundColor: '#198754',
                        pointBorderColor: '#fff',
                        pointBorderWidth: 2
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            usePointStyle: true,
                            padding: 15,
                            font: {
                                size: 12,
                                weight: '600'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: { size: 13, weight: 'bold' },
                        bodyFont: { size: 12 },
                        cornerRadius: 6,
                        displayColors: true
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            font: { size: 11 }
                        },
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        ticks: {
                            font: { size: 11 }
                        },
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }

    // Service Distribution Chart
    initServiceDistributionChart() {
        const canvas = document.getElementById('serviceChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        this.charts.service = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Deposits', 'Withdrawals', 'Loans', 'Account Opening', 'General Inquiry'],
                datasets: [{
                    data: [25, 20, 18, 22, 15],
                    backgroundColor: [
                        '#0d6efd',
                        '#198754',
                        '#ffc107',
                        '#0dcaf0',
                        '#6c757d'
                    ],
                    borderColor: '#fff',
                    borderWidth: 3
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: true,
                        position: 'right',
                        labels: {
                            padding: 15,
                            font: {
                                size: 12,
                                weight: '500'
                            }
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0, 0, 0, 0.8)',
                        padding: 12,
                        titleFont: { size: 13, weight: 'bold' },
                        bodyFont: { size: 12 },
                        cornerRadius: 6,
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                }
            }
        });
    }

    // Counter Performance Chart
    initCounterPerformanceChart() {
        const canvas = document.getElementById('counterChart');
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        
        this.charts.counter = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: ['Counter 1', 'Counter 2', 'Counter 3', 'Counter 4'],
                datasets: [
                    {
                        label: 'Tokens Served',
                        data: [45, 52, 38, 48],
                        backgroundColor: '#0d6efd'
                    },
                    {
                        label: 'Avg Service Time (min)',
                        data: [5, 6, 4, 5],
                        backgroundColor: '#6c757d'
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                indexAxis: 'y',
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    x: {
                        beginAtZero: true,
                        ticks: {
                            font: { size: 11 }
                        }
                    }
                }
            }
        });
    }

    // Destroy all charts
    destroy() {
        Object.values(this.charts).forEach(chart => {
            if (chart) chart.destroy();
        });
    }
}

// Initialize charts when page loads
document.addEventListener('DOMContentLoaded', function() {
    if (document.getElementById('dailyChart') || 
        document.getElementById('serviceChart') || 
        document.getElementById('counterChart')) {
        
        const chartsManager = new AnalyticsCharts();
        chartsManager.initCharts();

        // Cleanup on page unload
        window.addEventListener('beforeunload', function() {
            chartsManager.destroy();
        });
    }
});
