# Real-Time Features - Quick Reference Guide ⚡

## 🚀 Quick Start

### 1. Include Required Files
```html
<!-- CSS (already in base.html) -->
<link rel="stylesheet" href="{% static 'css/realtime-animations.css' %}">

<!-- JavaScript (already in base.html) -->
<script src="{% static 'js/skeleton-loader.js' %}"></script>
<script src="{% static 'js/realtime-manager.js' %}"></script>
```

### 2. Access Global Manager
```javascript
// Automatically initialized on page load
window.realtimeManager

// Access skeleton loader
window.SkeletonLoader
```

## 🎯 Common Usage Patterns

### Show Loading Skeleton
```javascript
const element = document.getElementById('content');
SkeletonLoader.showSkeleton(element, 'card');

// Replace with actual content
setTimeout(() => {
    SkeletonLoader.replaceSkeleton(element, actualContent);
}, 2000);
```

### Trigger Animations
```javascript
// Pulse animation
element.classList.add('pulse-animation');

// Token calling
element.classList.add('token-calling');

// Token completed
element.classList.add('token-completed');
```

### Show Notifications
```javascript
// Success
realtimeManager.showNotification('Done!', 'success');

// Error
realtimeManager.showNotification('Failed!', 'error');

// Warning
realtimeManager.showNotification('Warning!', 'warning');

// Info
realtimeManager.showNotification('Info!', 'info');
```

### Start Countdown Timer
```javascript
const timerElement = document.getElementById('timer');
realtimeManager.startCountdown(timerElement, 300, () => {
    console.log('Time up!');
});
```

### Call Token with Animation
```javascript
realtimeManager.callToken(tokenId, 'Counter 1');
```

## 📋 HTML Data Attributes

### Queue Status Updates
```html
<div data-queue-id="Q1">
    <div data-waiting-count>12</div>
    <div data-avg-wait>8 min</div>
</div>
```

### Token Status
```html
<div data-token-id="1001">
    <span data-token-status>Waiting</span>
</div>
```

## 🎨 CSS Classes

### Skeletons
- `.skeleton` - Base
- `.skeleton-text` - Text line
- `.skeleton-heading` - Heading
- `.skeleton-card` - Card shape
- `.skeleton-grid` - Multiple items

### Animations
- `.pulse-animation` - Token status change
- `.token-calling` - Calling animation
- `.token-completed` - Completion animation
- `.token-skipped` - Skip animation
- `.fade-in` / `.fade-out` - Fade effects

### Timers
- `.countdown-timer` - Base
- `.timer-warning` - Warning state
- `.timer-critical` - Critical state

### Toasts
- `.toast-success` - Green
- `.toast-error` - Red
- `.toast-warning` - Orange
- `.toast-info` - Blue

## 💡 Real-World Examples

### Example 1: Load Queue Status
```html
<div id="queue-container"></div>

<script>
// Show skeleton while loading
SkeletonLoader.showSkeleton(
    document.getElementById('queue-container'), 
    'card'
);

// Fetch data
fetch('/api/queue-status/')
    .then(r => r.json())
    .then(data => {
        // Replace skeleton with content
        SkeletonLoader.replaceSkeleton(
            document.getElementById('queue-container'),
            `<h3>Queue Status</h3><p>Waiting: ${data.waiting}</p>`
        );
    });
</script>
```

### Example 2: Call Token with Feedback
```html
<button onclick="callMyToken(1001)">Call Token</button>

<script>
function callMyToken(tokenId) {
    realtimeManager.callToken(tokenId, 'Counter 1');
    
    // Show announcement
    realtimeManager.triggerAnnouncement(tokenId, 'Counter 1');
    
    // Show notification
    realtimeManager.showNotification(
        `Your token has been called!`,
        'success'
    );
}
</script>
```

### Example 3: Animated Status Update
```html
<div class="status-badge" id="token-status">Waiting</div>

<script>
function updateStatus(newStatus) {
    const element = document.getElementById('token-status');
    
    // Add pulse animation
    element.classList.add('pulse-animation');
    
    // Update text
    element.textContent = newStatus;
    
    // Remove animation after completion
    setTimeout(() => {
        element.classList.remove('pulse-animation');
    }, 600);
}
</script>
```

### Example 4: Queue with Live Updates
```html
<div data-queue-id="Q1">
    <h3>Deposits Queue</h3>
    <p>Waiting: <strong data-waiting-count>0</strong></p>
    <p>Avg Wait: <strong data-avg-wait>0</strong> min</p>
</div>

<script>
// Auto-refresh every 5 seconds
// realtimeManager handles this automatically
// Just add data attributes and it works!
</script>
```

## 🔧 Configuration

```javascript
// Customize realtime manager
window.realtimeManager = new RealtimeManager({
    updateInterval: 5000,      // Refresh every 5 seconds
    autoRefresh: true,         // Enable auto-refresh
    animationDuration: 300     // Animation duration in ms
});
```

## 📱 Mobile Optimization

All animations and loaders automatically adjust for mobile:
- Reduced animation complexity on low-end devices
- Touch-friendly button sizes
- Responsive skeleton loaders
- Optimized notification positioning

## 🌓 Dark Mode

All components support dark mode automatically via `data-bs-theme="dark"` on html element:

```html
<!-- Dark mode -->
<html data-bs-theme="dark">
    ...
</html>

<!-- Light mode -->
<html data-bs-theme="light">
    ...
</html>
```

## ⚡ Performance Tips

1. **Limit skeleton loaders** - Show one at a time
2. **Batch animations** - Don't trigger too many at once
3. **Cache elements** - Store references if frequently accessed
4. **Debounce updates** - Limit update frequency
5. **Clean up** - Remove listeners when done

```javascript
// Good: Cache selector
const element = document.getElementById('token');
element.classList.add('pulse-animation');

// Bad: Repeated querying
for (let i = 0; i < 100; i++) {
    document.getElementById('token').classList.add('class');
}
```

## 🐛 Debugging

```javascript
// Enable console logging
realtimeManager.debug = true;

// Check if manager initialized
console.log(window.realtimeManager);

// List all active updates
console.log(realtimeManager.activeUpdates);

// List all notifications
console.log(realtimeManager.notifications);
```

## 📚 API Reference

### RealtimeManager Methods
```javascript
realtimeManager.startAutoRefresh()           // Start auto-refresh
realtimeManager.pauseAutoRefresh()           // Pause auto-refresh
realtimeManager.refreshQueueStatus()         // Manual refresh
realtimeManager.callToken(id, counter)       // Call token
realtimeManager.showNotification(msg, type)  // Show toast
realtimeManager.startCountdown(el, sec, cb)  // Start timer
realtimeManager.triggerAnnouncement(id, cnt) // Show announcement
```

### SkeletonLoader Methods
```javascript
SkeletonLoader.createTextSkeleton()    // Create text skeleton
SkeletonLoader.createCardSkeleton()    // Create card skeleton
SkeletonLoader.createTableSkeleton()   // Create table skeleton
SkeletonLoader.createGridSkeleton()    // Create grid skeleton
SkeletonLoader.createListSkeleton()    // Create list skeleton
SkeletonLoader.showSkeleton()          // Show in element
SkeletonLoader.replaceSkeleton()       // Replace with content
SkeletonLoader.hideSkeleton()          // Hide skeleton
```

## 🎓 Learning Path

1. **Start**: Read REALTIME_FEATURES.md
2. **Try**: Visit /demo/realtime/ page
3. **Implement**: Use examples above
4. **Customize**: Modify CSS in realtime-animations.css
5. **Integrate**: Add to your dashboards

## 🔗 Related Files

- `static/js/realtime-manager.js` - Core manager
- `static/js/skeleton-loader.js` - Skeleton utility
- `static/css/realtime-animations.css` - All animations
- `templates/demo/realtime-demo.html` - Demo page
- `REALTIME_FEATURES.md` - Full documentation

## 📞 Support

For issues or questions:
1. Check demo page for working examples
2. Review REALTIME_FEATURES.md
3. Check browser console for errors
4. Verify data attributes are correct

---

**Status:** ✅ Ready to Use | 📝 Well Documented | 🎯 Easy to Integrate

