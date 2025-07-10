#!/usr/bin/env python3
"""
Session Debug Script for Pacífico Workflow
Run this script to debug session issues and understand why users are getting logged out.
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'financiera.settings')
django.setup()

from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone

def check_sessions():
    """Check all sessions and identify potential issues"""
    print("🔍 Checking Django Sessions...")
    print("=" * 60)
    
    # Get all sessions
    all_sessions = Session.objects.all()
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
    
    print(f"Total sessions: {all_sessions.count()}")
    print(f"Active sessions: {active_sessions.count()}")
    print(f"Expired sessions: {expired_sessions.count()}")
    print()
    
    # Check active sessions
    if active_sessions.exists():
        print("📋 Active Sessions:")
        print("-" * 40)
        
        for session in active_sessions:
            try:
                data = session.get_decoded()
                user_id = data.get('_auth_user_id')
                
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        username = user.username
                    except User.DoesNotExist:
                        username = f"Unknown User (ID: {user_id})"
                else:
                    username = "Anonymous"
                
                time_until_expiry = session.expire_date - timezone.now()
                
                print(f"User: {username}")
                print(f"Session Key: {session.session_key}")
                print(f"Expires: {session.expire_date}")
                print(f"Time until expiry: {time_until_expiry}")
                print(f"Session Data Keys: {list(data.keys())}")
                print("-" * 20)
                
            except Exception as e:
                print(f"Error reading session {session.session_key}: {e}")
                print("-" * 20)
    
    # Check for potential issues
    print("\n🔍 Potential Issues:")
    print("-" * 40)
    
    # Check for sessions without user data
    orphaned_sessions = []
    for session in active_sessions:
        try:
            data = session.get_decoded()
            if '_auth_user_id' not in data:
                orphaned_sessions.append(session.session_key)
        except:
            orphaned_sessions.append(session.session_key)
    
    if orphaned_sessions:
        print(f"⚠️  Found {len(orphaned_sessions)} sessions without user data")
        for key in orphaned_sessions[:5]:  # Show first 5
            print(f"   - {key}")
        if len(orphaned_sessions) > 5:
            print(f"   ... and {len(orphaned_sessions) - 5} more")
    
    # Check for very old sessions
    old_sessions = active_sessions.filter(expire_date__gte=timezone.now() + timedelta(days=25))
    if old_sessions.exists():
        print(f"⚠️  Found {old_sessions.count()} sessions older than 25 days")
    
    # Check for sessions expiring soon
    soon_expiring = active_sessions.filter(
        expire_date__lte=timezone.now() + timedelta(hours=1)
    )
    if soon_expiring.exists():
        print(f"⚠️  Found {soon_expiring.count()} sessions expiring within 1 hour")
    
    print("\n✅ Session check completed!")

def cleanup_expired_sessions():
    """Clean up expired sessions"""
    print("🧹 Cleaning up expired sessions...")
    
    expired_count = Session.objects.filter(expire_date__lt=timezone.now()).count()
    if expired_count > 0:
        Session.objects.filter(expire_date__lt=timezone.now()).delete()
        print(f"✅ Cleaned up {expired_count} expired sessions")
    else:
        print("✅ No expired sessions to clean up")

def check_user_sessions(username):
    """Check sessions for a specific user"""
    print(f"👤 Checking sessions for user: {username}")
    print("-" * 40)
    
    try:
        user = User.objects.get(username=username)
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        
        user_sessions = []
        for session in sessions:
            data = session.get_decoded()
            user_id = data.get('_auth_user_id')
            if user_id and int(user_id) == user.id:
                user_sessions.append(session)
        
        if user_sessions:
            print(f"Found {len(user_sessions)} active sessions for {username}:")
            for session in user_sessions:
                time_until_expiry = session.expire_date - timezone.now()
                print(f"  - Session: {session.session_key}")
                print(f"    Expires: {session.expire_date}")
                print(f"    Time until expiry: {time_until_expiry}")
                print()
        else:
            print(f"No active sessions found for user {username}")
            
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "cleanup":
            cleanup_expired_sessions()
        elif command == "user" and len(sys.argv) > 2:
            check_user_sessions(sys.argv[2])
        else:
            print("Usage:")
            print("  python debug_session.py          # Check all sessions")
            print("  python debug_session.py cleanup  # Clean up expired sessions")
            print("  python debug_session.py user <username>  # Check specific user")
    else:
        check_sessions() 