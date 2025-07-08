from django.core.management.base import BaseCommand
from django.conf import settings
import os
from PIL import Image, ImageDraw, ImageFont

class Command(BaseCommand):
    help = 'Generate placeholder PWA icons'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Overwrite existing icons',
        )

    def handle(self, *args, **options):
        icon_sizes = [72, 96, 128, 144, 152, 192, 384, 512]
        icon_dir = os.path.join(settings.BASE_DIR, 'workflow', 'static', 'workflow', 'icons')
        
        # Ensure directory exists
        os.makedirs(icon_dir, exist_ok=True)
        
        self.stdout.write(f'Generating icons in: {icon_dir}')
        
        for size in icon_sizes:
            icon_path = os.path.join(icon_dir, f'icon-{size}x{size}.png')
            
            if os.path.exists(icon_path) and not options['force']:
                self.stdout.write(f'Skipping {icon_path} (already exists)')
                continue
            
            # Create a simple icon
            img = Image.new('RGB', (size, size), color='#009c3c')
            draw = ImageDraw.Draw(img)
            
            # Add a circle background
            margin = size // 8
            draw.ellipse([margin, margin, size-margin, size-margin], 
                        fill='#ffffff', outline='#007529', width=max(1, size//64))
            
            # Add text 'P'
            try:
                font_size = size // 2
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            text = 'P'
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = (size - text_width) // 2
            text_y = (size - text_height) // 2 - text_bbox[1]
            
            draw.text((text_x, text_y), text, fill='#009c3c', font=font)
            
            # Save the icon
            img.save(icon_path, 'PNG')
            self.stdout.write(f'Generated: {icon_path}')
        
        # Generate additional icons
        additional_icons = [
            ('apple-touch-icon.png', 180),
            ('favicon-32x32.png', 32),
            ('favicon-16x16.png', 16),
        ]
        
        for filename, size in additional_icons:
            icon_path = os.path.join(icon_dir, filename)
            
            if os.path.exists(icon_path) and not options['force']:
                self.stdout.write(f'Skipping {icon_path} (already exists)')
                continue
            
            # Create icon with same design
            img = Image.new('RGB', (size, size), color='#009c3c')
            draw = ImageDraw.Draw(img)
            
            margin = max(1, size // 8)
            draw.ellipse([margin, margin, size-margin, size-margin], 
                        fill='#ffffff', outline='#007529', width=max(1, size//64))
            
            try:
                font_size = max(8, size // 2)
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", font_size)
            except:
                font = ImageFont.load_default()
            
            text = 'P'
            text_bbox = draw.textbbox((0, 0), text, font=font)
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = (size - text_width) // 2
            text_y = (size - text_height) // 2 - text_bbox[1]
            
            draw.text((text_x, text_y), text, fill='#009c3c', font=font)
            
            img.save(icon_path, 'PNG')
            self.stdout.write(f'Generated: {icon_path}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully generated PWA icons!')
        )
