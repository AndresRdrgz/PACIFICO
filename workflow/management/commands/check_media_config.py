from django.core.management.base import BaseCommand
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Check media configuration and permissions'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🔍 Checking Media Configuration...'))
        
        # Check MEDIA_ROOT
        media_root = settings.MEDIA_ROOT
        self.stdout.write(f'📁 MEDIA_ROOT: {media_root}')
        
        if os.path.exists(media_root):
            self.stdout.write(self.style.SUCCESS('✅ MEDIA_ROOT exists'))
            
            # Check permissions
            try:
                os.access(media_root, os.R_OK)
                os.access(media_root, os.W_OK)
                self.stdout.write(self.style.SUCCESS('✅ MEDIA_ROOT is readable and writable'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ MEDIA_ROOT permission error: {e}'))
        else:
            self.stdout.write(self.style.WARNING('⚠️ MEDIA_ROOT does not exist, creating...'))
            try:
                os.makedirs(media_root, exist_ok=True)
                self.stdout.write(self.style.SUCCESS('✅ MEDIA_ROOT created successfully'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Failed to create MEDIA_ROOT: {e}'))
        
        # Check MEDIA_URL
        media_url = settings.MEDIA_URL
        self.stdout.write(f'🌐 MEDIA_URL: {media_url}')
        
        # Check DEBUG setting
        debug = settings.DEBUG
        self.stdout.write(f'🐛 DEBUG: {debug}')
        
        # Check file upload settings
        max_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 'Not set')
        self.stdout.write(f'📏 FILE_UPLOAD_MAX_MEMORY_SIZE: {max_size}')
        
        # Check allowed extensions
        allowed_extensions = getattr(settings, 'ALLOWED_MEDIA_EXTENSIONS', [])
        self.stdout.write(f'📄 Allowed extensions: {len(allowed_extensions)} types')
        
        # Test file creation
        test_file_path = os.path.join(media_root, 'test_config.txt')
        try:
            with open(test_file_path, 'w') as f:
                f.write('Media configuration test')
            self.stdout.write(self.style.SUCCESS('✅ Test file creation successful'))
            
            # Clean up
            os.remove(test_file_path)
            self.stdout.write(self.style.SUCCESS('✅ Test file cleanup successful'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Test file creation failed: {e}'))
        
        self.stdout.write(self.style.SUCCESS('🎉 Media configuration check completed!')) 