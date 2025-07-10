from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Debug session issues and show active sessions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--cleanup',
            action='store_true',
            help='Clean up expired sessions',
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Show sessions for specific user',
        )

    def handle(self, *args, **options):
        if options['cleanup']:
            self.cleanup_expired_sessions()
        
        if options['user']:
            self.show_user_sessions(options['user'])
        else:
            self.show_all_sessions()

    def cleanup_expired_sessions(self):
        """Clean up expired sessions"""
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
        count = expired_sessions.count()
        expired_sessions.delete()
        self.stdout.write(
            self.style.SUCCESS(f'Cleaned up {count} expired sessions')
        )

    def show_user_sessions(self, username):
        """Show sessions for a specific user"""
        try:
            user = User.objects.get(username=username)
            sessions = Session.objects.filter(expire_date__gte=timezone.now())
            
            user_sessions = []
            for session in sessions:
                data = session.get_decoded()
                user_id = data.get('_auth_user_id')
                if user_id and int(user_id) == user.id:
                    user_sessions.append({
                        'session_key': session.session_key,
                        'expire_date': session.expire_date,
                        'data': data
                    })
            
            if user_sessions:
                self.stdout.write(f'\nSessions for user "{username}":')
                for session in user_sessions:
                    self.stdout.write(f'  Session: {session["session_key"]}')
                    self.stdout.write(f'  Expires: {session["expire_date"]}')
                    self.stdout.write(f'  Data: {session["data"]}')
                    self.stdout.write('')
            else:
                self.stdout.write(f'No active sessions found for user "{username}"')
                
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" not found')
            )

    def show_all_sessions(self):
        """Show all active sessions"""
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        
        self.stdout.write(f'\nActive Sessions ({sessions.count()} total):')
        self.stdout.write('=' * 80)
        
        for session in sessions:
            data = session.get_decoded()
            user_id = data.get('_auth_user_id')
            
            if user_id:
                try:
                    user = User.objects.get(id=user_id)
                    username = user.username
                except User.DoesNotExist:
                    username = f'Unknown User (ID: {user_id})'
            else:
                username = 'Anonymous'
            
            time_until_expiry = session.expire_date - timezone.now()
            
            self.stdout.write(f'User: {username}')
            self.stdout.write(f'Session Key: {session.session_key}')
            self.stdout.write(f'Expires: {session.expire_date}')
            self.stdout.write(f'Time until expiry: {time_until_expiry}')
            self.stdout.write(f'Data: {data}')
            self.stdout.write('-' * 40)
        
        # Show session statistics
        total_sessions = Session.objects.count()
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now()).count()
        
        self.stdout.write(f'\nSession Statistics:')
        self.stdout.write(f'Total sessions: {total_sessions}')
        self.stdout.write(f'Active sessions: {sessions.count()}')
        self.stdout.write(f'Expired sessions: {expired_sessions}')
        
        if expired_sessions > 0:
            self.stdout.write(
                self.style.WARNING(f'Found {expired_sessions} expired sessions. Run with --cleanup to remove them.')
            ) 