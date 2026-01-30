# 🎨 BASE FRONTEND - ARCHITECTURE DIAGRAM

## Overall Page Layout

```
┌────────────────────────────────────────────────────────────────────┐
│                          NAVBAR (Sticky)                            │
│  🏦 Logo  │  Content  │  🔔(3)  │  🌙  │  👤 User ▼              │
└────────────────────────────────────────────────────────────────────┘
┌──────────────┬───────────────────────────────────────────────────────┐
│              │                                                         │
│   SIDEBAR    │                   MAIN CONTENT                        │
│              │                                                         │
│  🏠 Home     │  ┌────────────────────────────────────────────────┐  │
│  📊 Dashboard│  │ Page Title                                     │  │
│  🎫 Get Token│  │                                                │  │
│  🔍 Status   │  │  [Your Page Content]                          │  │
│  📜 History  │  │                                                │  │
│              │  │                                                │  │
│  ─────────   │  │                                                │  │
│  ❓ Help     │  │                                                │  │
│              │  └────────────────────────────────────────────────┘  │
└──────────────┴───────────────────────────────────────────────────────┘
```

## Responsive Behavior

### Desktop (>992px)
```
┌─────────────────────────────────────┐
│         NAVBAR                      │
├─────────────┬─────────────────────┤
│  SIDEBAR    │  MAIN CONTENT       │
│  (Fixed)    │  (Full width-280px) │
│             │                     │
└─────────────┴─────────────────────┘
```

### Tablet (768px - 992px)
```
┌─────────────────────────────────────┐
│         NAVBAR                      │
├─────────────────────────────────────┤
│        MAIN CONTENT                 │
│  (Sidebar becomes floating menu)    │
│                                     │
└─────────────────────────────────────┘
```

### Mobile (<768px)
```
┌──────────────────────────────────┐
│    NAVBAR (☰)                    │
├──────────────────────────────────┤
│   SIDEBAR (Off-canvas)           │
│   ┌─────────────────────────────┐│
│   │ Menu Item                   ││
│   │ Menu Item                   ││
│   │ Menu Item                   ││
│   └─────────────────────────────┘│
├──────────────────────────────────┤
│    MAIN CONTENT                  │
│                                  │
└──────────────────────────────────┘
```

## Notification System Flow

```
┌──────────────────────────────────────────┐
│     USER OPENS PAGE                      │
└──────────────────────────────────────────┘
                    │
                    ▼
┌──────────────────────────────────────────┐
│  DOM Ready → Initialize Components      │
│  - theme-toggle.js loads                │
│  - notifications.js loads               │
└──────────────────────────────────────────┘
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
┌──────────────────┐    ┌──────────────────┐
│  Theme Manager   │    │ Notification Mgr │
│  - Check store   │    │ - Fetch from API │
│  - Apply theme   │    │ - Update badge   │
│  - Listen toggle │    │ - Show dropdown  │
└──────────────────┘    └──────────────────┘
        │                       │
        ▼                       ▼
   [Every toggle]      [Every 30 seconds]
   Update theme        Fetch notifications
   Save preference      Update UI
```

## Dark Mode Toggle Flow

```
User Clicks Moon/Sun Icon
          │
          ▼
Get Current Theme from <html data-bs-theme="">
          │
          ▼
Toggle: light ↔ dark
          │
          ├─► Update <html data-bs-theme="dark">
          │
          ├─► Update localStorage['banking-app-theme']
          │
          ├─► Update Button Icon (moon ↔ sun)
          │
          └─► Dispatch CustomEvent('themechange')
          
All CSS respects [data-bs-theme="dark"] selector
CSS transitions apply smoothly
          │
          ▼
User Sees Theme Change Immediately
```

## Notification Dropdown Structure

```
Navbar Bell Icon (🔔)
          │
          ├─ Data Count (3) ← Badge
          │
          └─► Click Opens Dropdown
              
              ┌──────────────────────┐
              │ Notifications (350px) │
              ├──────────────────────┤
              │ 🔔 Token Called      │
              │ 1 minute ago         │
              │ Click to navigate    │
              ├──────────────────────┤
              │ ✓ Service Completed  │
              │ 5 minutes ago        │
              ├──────────────────────┤
              │ ⚠️  System Alert      │
              │ 15 minutes ago       │
              ├──────────────────────┤
              │ View all notifs → │  │
              └──────────────────────┘
              
Auto-refreshes every 30 seconds
```

## Sidebar Role Detection

```
User Logs In
    │
    ▼
Django Creates UserRole
    │
    ├─ customer
    ├─ staff
    ├─ counter_manager
    └─ admin
    
    │
    ▼
base.html Renders
    │
    └─► Check {% if user.userrole.role == 'customer' %}
        
        Customer View:              Staff View:
        ├─ 🏠 Home                 ├─ 🏠 Home
        ├─ 📊 Dashboard            ├─ 📊 Dashboard
        ├─ 🎫 Get Token            ├─ 📋 My Queue
        ├─ 🔍 Token Status         ├─ 📞 Serve Customer
        ├─ 📜 History              └─ 📈 Statistics
        └─ ❓ Help
        
        Admin View:
        ├─ 🏠 Home
        ├─ 📊 System Overview
        ├─ 👥 User Management
        ├─ 📊 Advanced Analytics
        ├─ 📄 Reports
        ├─ ⚙️ Settings
        └─ ❓ Help
```

## CSS Architecture

```
base.css (600+ lines)
│
├─► CSS Variables
│   ├─ Colors (primary, secondary, success, etc.)
│   ├─ Spacing (xs, sm, md, lg, xl, xxl)
│   ├─ Shadows (sm, md, lg)
│   ├─ Transitions (fast, base, slow)
│   └─ Border radius (sm, md, lg, xl)
│
├─► Global Styles
│   ├─ HTML/Body
│   ├─ Dark mode support
│   └─ Scrollbar styling
│
├─► Component Styles
│   ├─ Navbar
│   ├─ Sidebar
│   ├─ Cards
│   ├─ Buttons
│   ├─ Forms
│   ├─ Tables
│   ├─ Badges
│   ├─ Alerts
│   └─ Modals
│
├─► Responsive Design
│   ├─ Desktop (>992px)
│   ├─ Tablet (768-992px)
│   └─ Mobile (<768px)
│
├─► Utilities
│   ├─ Spacing
│   ├─ Text utilities
│   ├─ Shadows
│   ├─ Transitions
│   └─ Animations
│
└─► Accessibility
    ├─ Focus states
    ├─ Contrast
    ├─ Reduced motion
    └─ Keyboard navigation

notifications.css (300+ lines)
│
├─► Notification Dropdown
│   ├─ Container (350px)
│   ├─ Items styling
│   ├─ Icon colors
│   └─ Scrollbar
│
├─► Toast Notifications
│   ├─ Toast container
│   ├─ Toast styling
│   └─ Animations
│
└─► Dark Mode Support
    ├─ Dropdown colors
    ├─ Toast colors
    └─ Icon colors
```

## JavaScript Module Architecture

```
┌─────────────────────────────────┐
│      theme-toggle.js            │
├─────────────────────────────────┤
│ ThemeToggle Class               │
│  ├─ init()                      │
│  ├─ loadTheme()                 │
│  ├─ setTheme(theme)             │
│  ├─ toggle()                    │
│  ├─ getCurrentTheme()           │
│  ├─ isDarkMode()                │
│  └─ updateButtonIcon()          │
│                                 │
│ Auto-initializes on DOM ready   │
│ Exposes as window.themeToggle   │
└─────────────────────────────────┘

┌─────────────────────────────────┐
│     notifications.js            │
├─────────────────────────────────┤
│ NotificationsManager Class      │
│  ├─ init()                      │
│  ├─ fetchNotifications()        │
│  ├─ renderNotifications()       │
│  ├─ getNotificationIcon()       │
│  ├─ getTimeAgo()                │
│  ├─ updateBadge()               │
│  ├─ markAsRead()                │
│  ├─ getCsrfToken()              │
│  └─ showToast()                 │
│                                 │
│ Auto-initializes on DOM ready   │
│ Exposes as window.notifications │
│ Auto-refreshes every 30 seconds │
└─────────────────────────────────┘
```

## Dark Mode CSS Selector Pattern

```
Light Mode:
<html data-bs-theme="light">
    ↓
CSS applies standard colors
    
    .navbar { background-color: white; }
    .card { background-color: white; }
    .sidebar { background-color: #f8f9fa; }

Dark Mode:
<html data-bs-theme="dark">
    ↓
CSS applies dark colors
    
    [data-bs-theme="dark"] .navbar { background-color: #2d2d2d; }
    [data-bs-theme="dark"] .card { background-color: #2d2d2d; }
    [data-bs-theme="dark"] .sidebar { background-color: #1a1a1a; }
```

## Template Inheritance Chain

```
base.html (Foundation)
    │
    ├─► base/navbar.html (included)
    │       ├─ Brand
    │       ├─ Notification bell
    │       ├─ Theme toggle
    │       └─ User menu
    │
    ├─► base/sidebar.html (included)
    │       ├─ Common items
    │       ├─ Role-specific items
    │       └─ Help link
    │
    └─► {% block content %}
        
        └─► customer/dashboard.html (extends base)
        │   └─ Customer-specific content
        │
        └─► staff/serve_queue.html (extends base)
        │   └─ Staff-specific content
        │
        └─► admin/analytics.html (extends base)
            └─ Admin-specific content
```

## State Management

```
Browser Storage (localStorage)
│
└─ banking-app-theme: "light" | "dark"
   └─ Persists across sessions
   └─ Loaded on page init
   └─ Used to restore user preference

Browser API (Cookies)
│
└─ csrftoken: [CSRF token value]
   └─ Used for AJAX requests
   └─ Extracted by notifications.js

DOM State
│
├─ <html data-bs-theme="light|dark">
│  └─ Triggers CSS cascading
│  └─ Updated when user toggles
│
└─ #notificationBadge innerHTML
   └─ Updated on notification fetch
   └─ Shows unread count

Server (Not Stored Client-Side)
│
├─ User authentication
├─ UserRole assignment
├─ Notifications
└─ User preferences
```

## Event Flow Diagram

```
Page Load
    │
    ├─► DOMContentLoaded event
    │   ├─ Trigger theme-toggle.js init
    │   ├─ Trigger notifications.js init
    │   └─ Set notification timer
    │
    ├─► Window.themechange event (custom)
    │   └─ Dispatched when user toggles theme
    │   └─ Can trigger app-specific logic
    │
    └─► Fetch notifications every 30 seconds
        ├─ Call /api/notifications/
        ├─ Update badge count
        ├─ Render dropdown list
        └─ Repeat...

User Actions
    │
    ├─► Click notification bell
    │   └─ Show/hide dropdown (Bootstrap)
    │
    ├─► Click notification item
    │   ├─ Navigate to link
    │   └─ Mark as read (AJAX)
    │
    ├─► Click theme toggle
    │   ├─ Call toggle()
    │   ├─ Update theme
    │   ├─ Save to localStorage
    │   └─ Dispatch themechange event
    │
    └─► Click sidebar item
        └─ Navigate to page
        └─ Sidebar highlights active item
```

## File Dependency Graph

```
base.html
│
├─ Imports: Bootstrap CSS
├─ Imports: Font Awesome CSS
├─ Imports: static/css/base.css
├─ Imports: static/css/notifications.css
├─ Imports: static/css/dashboard.css
├─ Imports: static/css/animations.css
│
├─ Links: Bootstrap JS
├─ Links: jQuery
├─ Links: Chart.js
├─ Links: static/js/theme-toggle.js ────┐
├─ Links: static/js/notifications.js ────┤─► DOM manipulation
└─ Links: static/js/ui.js               └─► Event listeners

theme-toggle.js
│
├─ Reads from: localStorage
├─ Writes to: <html data-bs-theme="">
├─ Listens to: #themeToggle click
└─ Dispatches: window.themechange event

notifications.js
│
├─ Fetches from: /api/notifications/
├─ Updates: #notificationBadge
├─ Updates: #notificationList
├─ Reads from: CSRF cookie
└─ Timer: setInterval(30000ms)

CSS Cascade
│
base.css
    └─ Provides base variables and selectors
        
        ↓
        
[data-bs-theme="light|dark"] selectors
    └─ Override colors for theme
        
        ↓
        
notifications.css
    └─ Additional notification-specific styles
```

---

**This diagram shows the complete architectural foundation of your base frontend!** 🎨

See `BASE_FRONTEND_SUMMARY.md` for detailed documentation.
