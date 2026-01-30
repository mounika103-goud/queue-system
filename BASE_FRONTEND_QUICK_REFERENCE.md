# 🚀 BASE FRONTEND - QUICK REFERENCE

## Files Created/Modified

### Templates
- ✅ `templates/base/base.html` - Main layout template (280+ lines)

### Stylesheets  
- ✅ `static/css/base.css` - Foundation CSS (600+ lines)
- ✅ `static/css/notifications.css` - Notification styling (300+ lines)

### JavaScript
- ✅ `static/js/theme-toggle.js` - Dark/light mode (120+ lines)
- ✅ `static/js/notifications.js` - Notification system (280+ lines)

---

## Quick Features Overview

### 🔴 Navbar
```
┌─────────────────────────────────────────┐
│ 🏦 Queue Manager  │ 🔔 │ 🌙 │ 👤 User ▼ │
└─────────────────────────────────────────┘
  - Sticky at top
  - Responsive mobile menu
  - Real-time notification badge
  - Dark/light mode toggle
  - User dropdown with admin panel
```

### 📍 Sidebar
```
┌────────────────────┐
│ 👤 Customer        │
├────────────────────┤
│ 🏠 Home            │
│ 📊 Dashboard       │
│ 🎫 Get Token       │
│ 🔍 Token Status    │
│ 📜 History         │
├────────────────────┤
│ ❓ Help            │
└────────────────────┘
```
**Dynamically changes based on user role!**

### 🔔 Notifications
```
🔔 (3) ▼
├─ 🎫 Token Called (1m ago)
├─ ✓ Service Completed (5m ago)
├─ 📞 Counter Assigned (15m ago)
└─ View all notifications...
```
**Auto-refreshes every 30 seconds**

### 🌓 Dark Mode
```
Light: ☽ Moon icon (click to enable dark mode)
Dark:  ☀️ Sun icon  (click to enable light mode)
```
**Smooth transitions, persistent storage**

---

## How to Use in Your Pages

### 1. Create a New Page Template

```html
{% extends 'base/base.html' %}

{% block title %}Customer Dashboard{% endblock %}

{% block content %}
<div class="container-fluid">
    <div class="page-wrapper">
        <h1>Welcome to Dashboard</h1>
        <!-- Your content here -->
    </div>
</div>
{% endblock %}
```

### 2. Available CSS Classes

```html
<!-- Cards -->
<div class="card card-left-border success">
    <div class="card-header">Title</div>
    <div class="card-body">Content</div>
</div>

<!-- Buttons -->
<button class="btn btn-primary">Primary</button>
<button class="btn btn-icon"><i class="fas fa-save"></i></button>

<!-- Badges -->
<span class="badge badge-primary">New</span>
<span class="badge badge-success">Completed</span>

<!-- Alerts -->
<div class="alert alert-info">Info message</div>
<div class="alert alert-success">Success!</div>
<div class="alert alert-danger">Error occurred</div>

<!-- Tables -->
<table class="table">
    <thead>
        <tr>
            <th>Column 1</th>
            <th>Column 2</th>
        </tr>
    </thead>
    <tbody>
        <tr>
            <td>Data 1</td>
            <td>Data 2</td>
        </tr>
    </tbody>
</table>

<!-- Utilities -->
<div class="shadow-lg rounded-lg p-3">Elevated card</div>
<p class="text-truncate">Long text that...</p>
<a class="hover-lift">Hover effect</a>
```

### 3. Add Notifications (JavaScript)

```javascript
// Show a toast notification
notificationsManager.showToast(
    'Success!',
    'Your action was completed',
    'success',
    5000  // 5 seconds
);

// Available types: 'success', 'error', 'info', 'warning'
```

### 4. Listen to Theme Changes

```javascript
// React when user toggles theme
window.addEventListener('themechange', (event) => {
    const theme = event.detail.theme; // 'light' or 'dark'
    console.log('Theme changed to:', theme);
    
    // Update your charts, images, etc.
});
```

---

## CSS Variables Available

```css
/* Colors */
--primary-color: #0d6efd;
--secondary-color: #6c757d;
--success-color: #198754;
--danger-color: #dc3545;
--warning-color: #ffc107;
--info-color: #0dcaf0;

/* Spacing */
--spacing-xs: 0.25rem;
--spacing-sm: 0.5rem;
--spacing-md: 1rem;
--spacing-lg: 1.5rem;
--spacing-xl: 2rem;
--spacing-xxl: 3rem;

/* Shadows */
--shadow-sm: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
--shadow-md: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
--shadow-lg: 0 1rem 3rem rgba(0, 0, 0, 0.175);

/* Transitions */
--transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-base: 250ms cubic-bezier(0.4, 0, 0.2, 1);
--transition-slow: 350ms cubic-bezier(0.4, 0, 0.2, 1);
```

**Usage:**
```css
.my-element {
    padding: var(--spacing-lg);
    border-radius: var(--border-radius-lg);
    box-shadow: var(--shadow-md);
    transition: all var(--transition-base);
}
```

---

## Common Tasks

### Add a Page to Sidebar Menu

Edit `templates/base/base.html` and add to the appropriate role section:

```html
<!-- For customer role -->
{% if user.userrole.role == 'customer' %}
<li class="nav-item">
    <a class="nav-link" href="/customer/new-page/" data-page="newpage">
        <i class="fas fa-icon-name me-2"></i>New Page
    </a>
</li>
{% endif %}
```

### Change Theme Colors

Edit `static/css/base.css` and update `:root` variables:

```css
:root {
    --primary-color: #your-color;
    --success-color: #your-color;
    /* ... etc */
}
```

### Add Dark Mode Specific Styles

```css
[data-bs-theme="dark"] .my-element {
    background-color: var(--dark-surface);
    color: var(--dark-text);
}
```

### Create a Custom Modal

```html
<div class="modal fade" id="myModal" tabindex="-1">
    <div class="modal-dialog">
        <div class="modal-content">
            <div class="modal-header">
                <h5 class="modal-title">Title</h5>
                <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
            </div>
            <div class="modal-body">
                Content here
            </div>
            <div class="modal-footer">
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                <button type="button" class="btn btn-primary">Save</button>
            </div>
        </div>
    </div>
</div>
```

---

## Customization Tips

### 1. Change Primary Color
Edit `base.css` `:root`:
```css
--primary-color: #your-brand-color;
```

### 2. Update Logo/Brand
Edit `base.html` navbar brand:
```html
<a class="navbar-brand" href="/">
    <img src="..." alt="Logo"> Your Bank Name
</a>
```

### 3. Add More Notification Types
Edit `notifications.js` getNotificationIcon():
```javascript
const icons = {
    'your_type': 'fa-your-icon',
    // ...
};
```

### 4. Modify Sidebar Width
Edit `base.css`:
```css
.sidebar {
    width: 320px;  /* Change from 280px */
}
```

### 5. Change Notification Polling
Edit `notifications.js`:
```javascript
this.updateInterval = 60000;  // Change from 30000 (60 seconds)
```

---

## Browser Support

- ✅ Chrome (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Edge (latest)
- ✅ Mobile browsers

---

## Performance Notes

- ✅ Minimal JS bundle (notifications.js + theme-toggle.js)
- ✅ CSS optimized with variables
- ✅ Lazy-loading ready for child templates
- ✅ Notification polling configurable
- ✅ No external dependencies except Bootstrap

---

## Troubleshooting

### Navbar Dropdown Not Showing
- Check Bootstrap JS is loaded
- Verify data-bs-toggle="dropdown" is present
- Clear browser cache

### Dark Mode Not Working
- Check localStorage is enabled
- Verify base.css is loaded
- Check browser console for errors

### Sidebar Menu Items Not Visible
- Verify user.userrole.role is set correctly
- Check Django context variables
- Inspect HTML in browser dev tools

### Notifications Not Appearing
- Check API endpoint exists: `/api/notifications/`
- Verify CSRF token in browser console
- Check browser network tab for failed requests

---

## Next Steps

1. ✅ Create customer dashboard page
2. ✅ Create staff dashboard page
3. ✅ Create admin dashboard page
4. ✅ Create authentication pages
5. ✅ Implement API endpoints referenced in notifications.js

---

**Reference**: See `BASE_FRONTEND_SUMMARY.md` for complete details
**Version**: 1.0.0
**Status**: ✅ Ready for use
