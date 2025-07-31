#!/usr/bin/env python3
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from django.contrib.auth.models import User

# Create or update test user
username = 'testapi'
password = 'testpass123'

user, created = User.objects.get_or_create(username=username)
user.set_password(password)
user.is_superuser = True
user.is_staff = True
user.is_active = True
user.save()

if created:
    print(f"Created new user: {username}")
else:
    print(f"Updated existing user: {username}")

print(f"User {username} can login with password: {password}")
