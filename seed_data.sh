#!/bin/bash
# Quick setup script to seed realistic data into the dashboard

echo "========================================="
echo "Dashboard Data Seeding Script"
echo "========================================="
echo ""

# Check if we're in the right directory
if [ ! -f "manage.py" ]; then
    echo "ERROR: manage.py not found. Please run this script from the project root directory."
    exit 1
fi

echo "Step 1: Running seed_dashboard_data command..."
python manage.py seed_dashboard_data

echo ""
echo "Step 2: Collecting static files..."
python manage.py collectstatic --noinput

echo ""
echo "========================================="
echo "✓ Dashboard data seeding complete!"
echo "========================================="
echo ""
echo "You should now see realistic data in:"
echo "  • Admin Dashboard: /dashboard/admin/"
echo "  • Staff Dashboard: /dashboard/staff/"
echo "  • Customer Dashboard: /dashboard/"
echo ""
echo "Metrics will include:"
echo "  ✓ Average wait times"
echo "  ✓ Tokens served today"
echo "  ✓ Average service time"
echo "  ✓ System efficiency"
echo "  ✓ Queue status and load indicators"
echo ""
