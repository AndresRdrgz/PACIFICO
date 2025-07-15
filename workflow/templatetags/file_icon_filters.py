from django import template
import os

register = template.Library()

@register.filter
def get_file_icon(file_field):
    """
    Returns the appropriate FontAwesome icon class based on file extension
    """
    if not file_field:
        return 'fas fa-file-alt text-secondary'
    
    # Get the filename and extract extension
    filename = file_field.name if hasattr(file_field, 'name') else str(file_field)
    _, extension = os.path.splitext(filename.lower())
    
    # Define icon mappings
    icon_mappings = {
        # Documents
        '.pdf': 'fas fa-file-pdf text-danger',
        '.doc': 'fas fa-file-word text-primary',
        '.docx': 'fas fa-file-word text-primary',
        '.txt': 'fas fa-file-alt text-secondary',
        '.rtf': 'fas fa-file-alt text-secondary',
        
        # Spreadsheets
        '.xls': 'fas fa-file-excel text-success',
        '.xlsx': 'fas fa-file-excel text-success',
        '.csv': 'fas fa-file-csv text-success',
        
        # Presentations
        '.ppt': 'fas fa-file-powerpoint text-warning',
        '.pptx': 'fas fa-file-powerpoint text-warning',
        
        # Images
        '.jpg': 'fas fa-file-image text-info',
        '.jpeg': 'fas fa-file-image text-info',
        '.png': 'fas fa-file-image text-info',
        '.gif': 'fas fa-file-image text-info',
        '.bmp': 'fas fa-file-image text-info',
        '.svg': 'fas fa-file-image text-info',
        '.webp': 'fas fa-file-image text-info',
        
        # Archives
        '.zip': 'fas fa-file-archive text-warning',
        '.rar': 'fas fa-file-archive text-warning',
        '.7z': 'fas fa-file-archive text-warning',
        '.tar': 'fas fa-file-archive text-warning',
        '.gz': 'fas fa-file-archive text-warning',
        
        # Code/Text files
        '.html': 'fas fa-file-code text-info',
        '.htm': 'fas fa-file-code text-info',
        '.css': 'fas fa-file-code text-info',
        '.js': 'fas fa-file-code text-warning',
        '.json': 'fas fa-file-code text-warning',
        '.xml': 'fas fa-file-code text-info',
        '.py': 'fas fa-file-code text-primary',
        '.java': 'fas fa-file-code text-primary',
        '.cpp': 'fas fa-file-code text-primary',
        '.c': 'fas fa-file-code text-primary',
        '.php': 'fas fa-file-code text-primary',
        '.sql': 'fas fa-file-code text-primary',
        '.sh': 'fas fa-file-code text-success',
        '.bat': 'fas fa-file-code text-success',
        
        # Audio
        '.mp3': 'fas fa-file-audio text-info',
        '.wav': 'fas fa-file-audio text-info',
        '.flac': 'fas fa-file-audio text-info',
        '.aac': 'fas fa-file-audio text-info',
        
        # Video
        '.mp4': 'fas fa-file-video text-danger',
        '.avi': 'fas fa-file-video text-danger',
        '.mov': 'fas fa-file-video text-danger',
        '.wmv': 'fas fa-file-video text-danger',
        '.flv': 'fas fa-file-video text-danger',
        '.mkv': 'fas fa-file-video text-danger',
        
        # CAD/Design
        '.dwg': 'fas fa-drafting-compass text-primary',
        '.dxf': 'fas fa-drafting-compass text-primary',
        '.ai': 'fas fa-palette text-warning',
        '.psd': 'fas fa-palette text-info',
        '.eps': 'fas fa-palette text-info',
        
        # Certificates
        '.pem': 'fas fa-certificate text-success',
        '.crt': 'fas fa-certificate text-success',
        '.key': 'fas fa-key text-warning',
        
        # Database
        '.db': 'fas fa-database text-primary',
        '.sqlite': 'fas fa-database text-primary',
        '.mdb': 'fas fa-database text-primary',
        
        # Logs
        '.log': 'fas fa-clipboard-list text-secondary',
        
        # Config files
        '.ini': 'fas fa-cog text-secondary',
        '.conf': 'fas fa-cog text-secondary',
        '.config': 'fas fa-cog text-secondary',
        '.yml': 'fas fa-cog text-secondary',
        '.yaml': 'fas fa-cog text-secondary',
    }
    
    # Return the appropriate icon or default
    return icon_mappings.get(extension, 'fas fa-file-alt text-secondary')

@register.filter
def get_file_extension(file_field):
    """
    Returns just the file extension (without the dot)
    """
    if not file_field:
        return ''
    
    filename = file_field.name if hasattr(file_field, 'name') else str(file_field)
    _, extension = os.path.splitext(filename.lower())
    return extension[1:] if extension else ''  # Remove the dot

@register.filter
def get_file_name(file_field):
    """
    Returns just the filename without path
    """
    if not file_field:
        return ''
    
    filename = file_field.name if hasattr(file_field, 'name') else str(file_field)
    return os.path.basename(filename)

@register.filter
def get_file_size(file_field):
    """
    Returns human-readable file size
    """
    if not file_field or not hasattr(file_field, 'size'):
        return ''
    
    try:
        size = file_field.size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    except:
        return '' 