# Real-Time Frontend Features ⚡

## Overview

Comprehensive real-time frontend system with live updates, animations, skeleton loaders, and countdown timers. Built with vanilla JavaScript for compatibility with future Django Channels WebSocket integration.

## Features Implemented

### 1. **Live Queue Updates** 📊
- Auto-refresh queue status every 5 seconds
- Smooth fade animations on data changes
- Real-time waiting customer counts
- Average wait time calculations
- Queue status indicators (Normal/Busy/Critical)

**Usage:**
```javascript
// Auto-refresh starts automatically
// Customize refresh interval:
window.realtimeManager = new RealtimeManager({
    updateInterval: 3000,  // 3 seconds
    autoRefresh: true
});
```

### 2. **Animated Token Calling** 🎬
- Call token with smooth animations
- Counter assignment visualization
- Pulsing effect on token status change
- Success/error notifications
- Auto-announcement to customers

**Usage:**
```javascript
// Call a token with animation
realtimeManager.callToken(tokenId, 'Counter 1');

// Manual animation trigger
document.getElementById('token').classList.add('token-calling');
```

### 3. **Skeleton Loaders** ⌛
Premium loading states with smooth transitions. Supports multiple loader types:

**Available Loaders:**
```javascript
// Text skeleton (3 lines)
SkeletonLoader.showSkeleton(element, 'text', {
    lines: 3,
    width: '100%'
});

// Card skeleton
SkeletonLoader.showSkeleton(element, 'card');

// KPI card skeleton
SkeletonLoader.showSkeleton(element, 'kpi');

// Table skeleton (5 rows, 4 columns)
SkeletonLoader.showSkeleton(element, 'table', {
    rows: 5,
    cols: 4
});

// Grid skeleton (6 items)
SkeletonLoader.showSkeleton(element, 'grid', {
    items: 6
});

// List skeleton (5 items)
SkeletonLoader.showSkeleton(element, 'list', {
    items: 5
});
```

**Replace Skeleton with Content:**
```javascript
// Show skeleton
SkeletonLoader.showSkeleton(element, 'card');

// After loading
setTimeout(() => {
    SkeletonLoader.replaceSkeleton(element, '<div>Loaded content</div>');
}, 2000);
```

### 4. **Countdown Timers** ⏱️
Real-time countdown with visual warnings:

**Usage:**
```javascript
const timerElement = document.getElementById('countdown');
const timerId = realtimeManager.startCountdown(timerElement, 300, () => {
    console.log('Time expired!');
});

// Format: MM:SS
// Adds warning class when < 10 seconds
```

**CSS Classes:**
- `.countdown-timer` - Base style
- `.timer-warning` - Applied when < 10 seconds (orange pulse)
- `.timer-critical` - Applied when < 5 seconds (red pulse)

### 5. **Pulse Animations** 💫
Visual feedback for token status changes:

**Classes:**
```html
<!-- Single pulse on status change -->
<div class="pulse-animation">Content</div>

<!-- Continuous pulse -->
<div class="pulse-continuous">Content</div>

<!-- Status change pulse (green) -->
<div class="status-change-pulse">Token Updated</div>
```

**Trigger Programmatically:**
```javascript
const element = document.getElementById('token');
element.classList.add('pulse-animation');

// Auto-remove after animation
setTimeout(() => {
    element.classList.remove('pulse-animation');
}, 600);
```

### 6. **Toast Notifications** 🔔
Elegant notification system with auto-dismiss:

**Usage:**
```javascript
// Success notification
realtimeManager.showNotification('✓ Token called successfully!', 'success');

// Error notification
realtimeManager.showNotification('✕ Failed to process', 'error');

// Warning notification
realtimeManager.showNotification('⚠ Queue is busy', 'warning');

// Info notification
realtimeManager.showNotification('ⓘ New customer arrived', 'info');
```

**Types:**
- `success` - Green gradient background
- `error` - Red gradient background
- `warning` - Orange gradient background
- `info` - Blue gradient background

**Auto-dismiss:** 4 seconds

### 7. **Announcement Badge** 📣
Large announcement for token calling:

**Usage:**
```javascript
// Automatically triggered by callToken()
realtimeManager.triggerAnnouncement(tokenId, 'Counter 1');
```

## Files Created

### JavaScript Files
1. **`static/js/realtime-manager.js`** (550+ lines)
   - Core real-time manager class
   - Auto-refresh logic
   - Token update detection
   - Animation triggers
   - Notification system

2. **`static/js/skeleton-loader.js`** (350+ lines)
   - Skeleton loader factory
   - Multiple loader types
   - Smooth transitions
   - Content replacement

### CSS Files
1. **`static/css/realtime-animations.css`** (800+ lines)
   - Skeleton loader styles
   - Pulse animations
   - Token animations
   - Toast notifications
   - Countdown timer styles
   - Announcement badge styles
   - Dark mode support
   - Responsive design

### Template Files
1. **`templates/demo/realtime-demo.html`** (300+ lines)
   - Interactive demo page
   - All features demonstrated
   - Live examples
   - Code snippets

### Views & URLs
1. **Updated `views.py`** - Added demo view
2. **Updated `urls.py`** - Added demo route

## CSS Class Reference

### Skeleton Loaders
```css
.skeleton              /* Base skeleton */
.skeleton-text        /* Text line skeleton */
.skeleton-heading     /* Heading skeleton */
.skeleton-card        /* Card skeleton */
.skeleton-avatar      /* Round avatar skeleton */
.skeleton-button      /* Button skeleton */
.skeleton-input       /* Input field skeleton */
.skeleton-grid        /* Grid layout skeletons */
```

### Animations
```css
.pulse-animation      /* Token status change pulse */
.pulse-continuous     /* Continuous pulsing */
.status-change-pulse  /* Green status pulse */
.token-calling        /* Token calling animation */
.token-accepted       /* Token accepted animation */
.token-completed      /* Token completion animation */
.token-skipped        /* Token skip animation */
```

### Notifications
```css
.toast                /* Base toast */
.toast-success        /* Success toast */
.toast-error          /* Error toast */
.toast-warning        /* Warning toast */
.toast-info           /* Info toast */
.animate-slideIn      /* Slide in animation */
.fade-out             /* Fade out animation */
```

### Timers
```css
.countdown-timer      /* Base timer */
.timer-warning        /* Warning state (< 10s) */
.timer-critical       /* Critical state (< 5s) */
```

## Integration with Dashboards

### Customer Dashboard
```html
<!-- Live token status with animation -->
<div class="pulse-animation" data-token-id="1001">
    <h4>Your Token: 1001</h4>
    <p data-token-status>Waiting</p>
</div>

<!-- Countdown timer -->
<div class="countdown-timer" id="wait-timer">05:00</div>
```

### Staff Dashboard
```html
<!-- Queue status with auto-refresh -->
<div data-queue-id="Q1">
    <div data-waiting-count>12</div>
    <div data-avg-wait>8 min</div>
</div>

<!-- Token calling with animation -->
<button onclick="realtimeManager.callToken(1001, 'Counter 1')">
    Call Token
</button>
```

### Admin Dashboard
```html
<!-- KPI cards with skeleton loaders -->
<div id="kpi-avg-wait">
    <!-- Skeleton shows while loading -->
</div>

<!-- Announcement badge for announcements -->
<div data-announcement-container></div>
```

## Performance Features

✅ **Optimized Updates**
- Only refreshes visible elements
- Pauses on page invisible (tab blur)
- Efficient DOM manipulation
- Debounced animations

✅ **Memory Management**
- Automatic cleanup on unload
- Event listener cleanup
- Timer management
- Notification auto-dismiss

✅ **Animation Performance**
- Hardware-accelerated CSS animations
- RequestAnimationFrame where applicable
- Minimal repaints/reflows
- Efficient class toggling

## Dark Mode Support

All components fully support dark mode:
```css
[data-bs-theme="dark"] .skeleton { ... }
[data-bs-theme="dark"] .toast { ... }
[data-bs-theme="dark"] .countdown-timer { ... }
```

## Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+
- ✅ Mobile browsers

## Future Enhancements

### Phase 2: Django Channels Integration
```javascript
// WebSocket connection (future)
const socket = new WebSocket('ws://localhost/ws/queue/');
socket.onmessage = (event) => {
    const data = JSON.parse(event.data);
    realtimeManager.updateQueueDisplay(data);
};
```

### Phase 3: Service Workers
- Offline support
- Background sync
- Push notifications

### Phase 4: Advanced Features
- Voice announcements
- Mobile notifications
- Analytics tracking
- Performance monitoring

## Demo Page

Access the interactive demo:
```
http://localhost:8000/demo/realtime/
```

Features showcase:
- Skeleton loader examples
- Animation triggers
- Toast notifications
- Timer examples
- Live queue updates

## Accessibility

✅ Semantic HTML
✅ ARIA labels on interactive elements
✅ Keyboard navigation support
✅ Screen reader friendly
✅ High contrast dark mode
✅ Reduced motion support (future)

## Troubleshooting

### Animations not showing
```javascript
// Check if element exists
console.log(document.querySelector('[data-token-id]'));

// Force animation
element.classList.remove('pulse-animation');
setTimeout(() => element.classList.add('pulse-animation'), 10);
```

### Skeleton loaders not replacing
```javascript
// Check for proper element targeting
const element = document.getElementById('my-container');
SkeletonLoader.replaceSkeleton(element, '<div>Content</div>');
```

### Timers not stopping
```javascript
// Manually clear timer if needed
clearInterval(timerHandle);
```

## Code Examples

### Complete Example: Update Customer Token Status
```javascript
async function updateTokenStatus(tokenId) {
    const element = document.querySelector(`[data-token-id="${tokenId}"]`);
    
    // Show skeleton while loading
    SkeletonLoader.showSkeleton(element, 'card');
    
    try {
        const response = await fetch(`/api/token/${tokenId}/`);
        const data = await response.json();
        
        // Replace skeleton with actual content
        SkeletonLoader.replaceSkeleton(element, `
            <h4>Token: ${data.token_number}</h4>
            <p>Status: ${data.status}</p>
            <div class="countdown-timer" id="timer-${tokenId}"></div>
        `);
        
        // Trigger pulse animation
        element.classList.add('pulse-animation');
        
        // Start countdown
        const timerElement = document.getElementById(`timer-${tokenId}`);
        realtimeManager.startCountdown(timerElement, data.estimated_wait * 60);
        
        // Show notification
        realtimeManager.showNotification(
            `Token ${data.token_number} status updated to ${data.status}`,
            'info'
        );
    } catch (error) {
        realtimeManager.showNotification('Failed to update token', 'error');
    }
}
```

## License & Credits

Built with vanilla JavaScript - no external animation libraries required.
Ready for Django Channels WebSocket integration.

---

**Status:** ✅ Production Ready | 📱 Mobile Optimized | 🌓 Dark Mode | ⚡ Performance Optimized

