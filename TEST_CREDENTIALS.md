# 🔐 TEST CREDENTIALS

## Quick Access to Dashboard

### Admin Account
- **Username**: `admin`
- **Password**: `admin123`
- **URL**: `http://localhost:8000/admin-dashboard/`

### Staff Account
- **Username**: `staff1`
- **Password**: `staff123`
- **URL**: `http://localhost:8000/staff-dashboard/`

### Customer Account
- **Username**: `customer1`
- **Password**: `customer123`
- **URL**: `http://localhost:8000/customer-dashboard/`

---

## 🚀 Getting Started

### Step 1: Start the Django Server
```bash
python manage.py runserver
```

Server will run at: `http://localhost:8000`

### Step 2: Go to Login
```
http://localhost:8000/login/
```

### Step 3: Use One of the Credentials Above
Choose based on which dashboard you want to see:
- **Admin** → System analytics & all queues
- **Staff** → Counter operations & service metrics
- **Customer** → Your tokens & waiting status

### Step 4: Access Features
Once logged in, you'll see:
- ✅ Live queue updates (auto-refresh every 5 seconds)
- ✅ Skeleton loaders (smooth loading states)
- ✅ Animations (pulse, token calling, etc.)
- ✅ Countdown timers (with warning/critical states)
- ✅ Toast notifications
- ✅ Interactive charts (admin dashboard)

---

## 📊 Available Dashboards

### Customer Dashboard (`/customer-dashboard/`)
- Your tokens & status
- Wait time estimate
- Queue position
- Service history
- Real-time updates

### Staff Dashboard (`/staff-dashboard/`)
- Counter status
- Tokens served today
- Average service time
- Waiting customers count
- Counter performance metrics

### Admin Dashboard (`/admin-dashboard/`)
- System KPIs
- Average wait time
- Tokens processed
- Queue heatmap
- Real-time alerts
- Recommendations
- Interactive charts & filters

---

## 🔄 If Accounts Don't Exist

Run the initialization command:
```bash
python manage.py init_data
```

This will create:
- 1 Admin user (admin/admin123)
- 3 Staff users (staff1-3/staff123)
- 5 Customer users (customer1-5/customer123)
- 3 Counters (C1, C2, C3)
- 5 Service Queues

---

## 🧪 Demo Pages

### Real-Time Features Demo
```
http://localhost:8000/demo/realtime/
```
See all real-time features in action:
- Skeleton loaders showcase
- Animation demonstrations
- Live queue status
- Interactive examples

### Analytics Demo (Coming Soon)
```
http://localhost:8000/demo/analytics/
```

---

## 🐛 Troubleshooting

### Error: "User role not configured"
→ Run `python manage.py init_data` to initialize accounts

### Server won't start
→ Check if port 8000 is in use: `python manage.py runserver 8001`

### Login not working
→ Ensure migrations are applied: `python manage.py migrate`

### No data showing in dashboards
→ Run `python manage.py init_data` to populate test data

---

## 📱 Browser Support

✅ Chrome 90+
✅ Firefox 88+
✅ Safari 14+
✅ Edge 90+
✅ Mobile browsers

---

**Ready to go?** Open `http://localhost:8000/login/` and log in! 🚀
