#!/usr/bin/env python3
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from django.contrib.auth.models import User

print("Available users:")
for user in User.objects.all():
    print(f"  Username: {user.username}, Superuser: {user.is_superuser}, Active: {user.is_active}")
