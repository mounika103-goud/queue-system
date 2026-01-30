#!/usr/bin/env python
"""
Reset database and create fresh schema
"""
import os
import django
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')

# Delete old database
db_file = 'db.sqlite3'
if os.path.exists(db_file):
    try:
        os.remove(db_file)
        print(f"✓ Deleted old database: {db_file}")
    except Exception as e:
        print(f"✗ Could not delete database: {e}")

# Delete old migrations
migrations_dir = 'queueapp/migrations'
if os.path.exists(migrations_dir):
    for file in os.listdir(migrations_dir):
        if file.startswith('000') and file.endswith('.py'):
            path = os.path.join(migrations_dir, file)
            try:
                os.remove(path)
                print(f"✓ Deleted migration: {file}")
            except Exception as e:
                print(f"✗ Could not delete {file}: {e}")

# Delete pycache
pycache_dir = os.path.join(migrations_dir, '__pycache__')
if os.path.exists(pycache_dir):
    try:
        shutil.rmtree(pycache_dir)
        print(f"✓ Deleted __pycache__")
    except Exception as e:
        print(f"✗ Could not delete __pycache__: {e}")

print("\n✓ Database reset complete!")
print("Run these commands next:")
print("  python manage.py makemigrations queueapp")
print("  python manage.py migrate")
print("  python setup_accounts.py")
