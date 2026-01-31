#!/usr/bin/env python
"""Fix token timestamps where generated_at > called_at"""

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'queueproject.settings')
django.setup()

from queueapp.models import Token
from django.utils import timezone
from datetime import timedelta

# Find all tokens where generated_at > called_at
problematic_tokens = Token.objects.filter(
    called_at__isnull=False
).exclude(generated_at__lte=timezone.now())

print(f"Checking all tokens...")

count = 0
for token in Token.objects.filter(called_at__isnull=False):
    if token.generated_at > token.called_at:
        count += 1
        print(f"Token {token.token_number}:")
        print(f"  Before - generated_at: {token.generated_at}, called_at: {token.called_at}")
        
        # Fix: set called_at to be generated_at + random wait between 2-10 minutes
        import random
        wait_minutes = random.randint(2, 10)
        token.called_at = token.generated_at + timedelta(minutes=wait_minutes)
        
        # Also fix service times if they exist
        if token.service_started_at and token.service_ended_at:
            if token.service_started_at < token.called_at:
                token.service_started_at = token.called_at + timedelta(minutes=random.randint(0, 2))
            if token.service_ended_at < token.service_started_at:
                service_duration = random.randint(3, 15)  # 3-15 minutes service
                token.service_ended_at = token.service_started_at + timedelta(minutes=service_duration)
        
        token.save()
        print(f"  After  - generated_at: {token.generated_at}, called_at: {token.called_at}")
        print()

print(f"Fixed {count} tokens with incorrect timestamps")
