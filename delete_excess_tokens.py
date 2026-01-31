#!/usr/bin/env python
import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from queueapp.models import Token

# Get total count
total_tokens = Token.objects.count()
print(f"Total tokens in database: {total_tokens}")

# Keep 20 most recent tokens
keep_count = 20
if total_tokens <= keep_count:
    print(f"Already have {total_tokens} tokens (less than or equal to {keep_count}). No deletion needed.")
else:
    # Get IDs of the 20 most recent tokens
    tokens_to_keep = Token.objects.order_by('-created_at')[:keep_count]
    keep_ids = set(tokens_to_keep.values_list('id', flat=True))
    
    # Delete all others
    tokens_to_delete = Token.objects.exclude(id__in=keep_ids)
    delete_count = tokens_to_delete.count()
    
    print(f"\nKeeping {keep_count} most recent tokens (IDs: {sorted(keep_ids)})")
    print(f"Deleting {delete_count} tokens...")
    
    tokens_to_delete.delete()
    
    remaining = Token.objects.count()
    print(f"\nDeletion complete!")
    print(f"Remaining tokens: {remaining}")
