# 🚀 GETTING STARTED - Complete Setup Guide

## ⚡ Quick Start (5 minutes)

### 1️⃣ Open Terminal in Project Directory
```bash
cd c:\Users\priya\OneDrive\Documents\EY_4.0_sphn\projectey
```

### 2️⃣ Create Test Accounts & Initialize Data
```bash
python setup_accounts.py
```

You'll see:
```
✓ Created admin user (admin/admin123)
✓ Staff users already exist
✓ Customer users already exist
✓ Counters already exist
✓ Queues already exist

✅ Setup Complete!
```

### 3️⃣ Start Django Server
```bash
python manage.py runserver
```

Server output:
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### 4️⃣ Log In to Dashboard
Open browser: `http://localhost:8000/accounts/login/`

---

## 🔐 Login Credentials

### Admin Dashboard (System Overview)
```
Username: admin
Password: admin123
URL: http://localhost:8000/dashboard/admin/
```
**What you'll see:**
- System-wide KPIs
- Real-time queue status
- Interactive charts
- Performance analytics
- Alerts & recommendations

### Staff Dashboard (Counter Operations)
```
Username: staff1
Password: staff123
URL: http://localhost:8000/dashboard/staff/
```
**What you'll see:**
- Counter status
- Tokens served today
- Waiting customers
- Service metrics
- Real-time updates

### Customer Dashboard (Token Tracking)
```
Username: customer1
Password: customer123
URL: http://localhost:8000/dashboard/customer/
```
**What you'll see:**
- Your tokens
- Wait time estimate
- Service status
- History
- Real-time updates

---

## 📊 Available Demo Pages

### Real-Time Features Demo
```
http://localhost:8000/demo/realtime/
```
**Features:**
- ⏳ Skeleton loaders (6 types)
- 💫 Animations showcase
- ⏱️ Countdown timers
- 🔔 Toast notifications
- 📊 Live queue status

### Admin Dashboard Features
```
http://localhost:8000/dashboard/admin/
```
**Features:**
- 📈 Interactive charts
- 🎛️ Real-time filters
- 📊 KPI cards
- 🔥 Queue heatmap
- ⚡ Alerts system
- 💡 Smart recommendations

---

## 🔧 Troubleshooting

### ❌ Port 8000 Already in Use
```bash
# Use a different port
python manage.py runserver 8001
```
Then visit: `http://localhost:8001/accounts/login/`

### ❌ "User role not configured" Error
```bash
# Re-initialize accounts
python setup_accounts.py
```

### ❌ Database Error
```bash
# Apply migrations
python manage.py migrate
# Then initialize data
python setup_accounts.py
```

### ❌ Static Files Not Loading
```bash
# Collect static files
python manage.py collectstatic --noinput
```

### ❌ Can't See Real-Time Updates
1. ✅ Make sure you're logged in
2. ✅ Check the browser console (F12) for errors
3. ✅ Ensure server is running
4. ✅ Try refreshing the page (Ctrl+R)

---

## 📁 Project Structure

```
projectey/
├── manage.py                 ← Django management script
├── setup_accounts.py         ← Account initialization (RUN THIS)
├── TEST_CREDENTIALS.md       ← Login credentials
├── requirements.txt          ← Python dependencies
├── db.sqlite3               ← Database
│
├── queueproject/            ← Project settings
│   ├── settings.py
│   ├── urls.py             ← Main URL routing
│   └── wsgi.py
│
├── queueapp/                ← Main app
│   ├── models.py           ← Database models
│   ├── views.py            ← View logic
│   ├── urls.py             ← App URL routing
│   ├── permissions.py      ← Role-based access
│   ├── api.py              ← API endpoints
│   ├── services.py         ← Business logic
│   ├── utils.py            ← Helper functions
│   └── management/
│       └── commands/
│           └── init_data.py ← Alternative setup
│
├── static/                  ← Static files
│   ├── js/
│   │   ├── realtime-manager.js      ← Live updates
│   │   ├── skeleton-loader.js       ← Loading states
│   │   └── ...
│   ├── css/
│   │   ├── realtime-animations.css  ← Animations
│   │   └── ...
│   └── images/
│
└── templates/              ← HTML templates
    ├── base.html           ← Base template
    ├── login.html          ← Login page
    ├── customer/           ← Customer dashboard
    ├── staff/              ← Staff dashboard
    ├── admin/              ← Admin dashboard
    ├── demo/               ← Demo pages
    └── ...
```

---

## ✨ Features Included

### ✅ Real-Time Features
- Auto-refresh every 5 seconds
- Skeleton loaders (smooth loading)
- Pulse animations
- Countdown timers
- Toast notifications
- Announcement badges

### ✅ Interactive Dashboards
- Customer Dashboard (track tokens)
- Staff Dashboard (manage queues)
- Admin Dashboard (system overview)

### ✅ Modern Design
- Dark mode support
- Responsive layout
- Smooth animations
- Premium styling
- Glassmorphism effects

### ✅ Security
- User authentication
- Role-based access control
- CSRF protection
- Secure API endpoints

---

## 🎯 Next Steps After Login

### As Admin:
1. Visit Admin Dashboard
2. See real-time queue status
3. View system analytics
4. Monitor performance metrics
5. Check alerts & recommendations

### As Staff:
1. Visit Staff Dashboard
2. See assigned counter
3. View waiting tokens
4. Monitor service metrics
5. Call next customer

### As Customer:
1. Visit Customer Dashboard
2. Generate new token
3. Track token status
4. See wait time estimate
5. View service history

---

## 🆘 Need Help?

### Check These Files:
- **Credentials**: [TEST_CREDENTIALS.md](TEST_CREDENTIALS.md)
- **Real-Time Guide**: [REALTIME_QUICK_REFERENCE.md](REALTIME_QUICK_REFERENCE.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Project Summary**: [PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)

### Common Commands:
```bash
# Start server
python manage.py runserver

# Create test data
python setup_accounts.py

# Alternative data init
python manage.py init_data

# Apply migrations
python manage.py migrate

# Create new migration
python manage.py makemigrations

# Admin panel
http://localhost:8000/admin/
```

---

## 🚀 You're All Set!

Your Smart Banking Queue Management System is ready to use!

1. ✅ Run `python setup_accounts.py`
2. ✅ Run `python manage.py runserver`
3. ✅ Visit `http://localhost:8000/accounts/login/`
4. ✅ Use credentials from [TEST_CREDENTIALS.md](TEST_CREDENTIALS.md)
5. ✅ Enjoy your dashboard! 🎉

---

**Questions?** Check the documentation files or review the code comments!

Last Updated: January 29, 2026
